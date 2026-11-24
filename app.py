# app.py
"""
Backend for the side-business canvas study.

Flow (participants arrive from Prolific/Qualtrics with ?pid=...):
  /study  assigns the condition (canvas_ai or canvas_noai, balanced randomisation) -> /intro
  /intro  start page: the participant enters an idea of their own (the five ideas are examples only), then the task
  /canvas the slide (Lean Canvas for side businesses); AI co-founder panel in canvas_ai only
  /done   thank-you, then redirect to the survey (SURVEY_URL)

Data (SQLite): participants, canvas (final text), canvas_log (every autosaved change), messages (AI chat), events.
Researcher exports: /admin/export/<name>.csv?token=...  and the slide view /admin/slide/<pid>?token=...

Run locally: python app.py (mock AI without an API key).  Production: gunicorn -w 2 -b 0.0.0.0:8000 app:app
"""
import csv
import hmac
import io
import json
import os
import re
import secrets
import sqlite3
import sys
import time
from urllib.parse import quote

from flask import Flask, Response, abort, g, jsonify, redirect, render_template, request, url_for

import content
import llm
import randomisation
from prompts import parse_reply, system_prompt

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "study.db"))
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "")
FRAME_ANCESTORS = os.environ.get("FRAME_ANCESTORS", "'self' https://*.qualtrics.com https://*.prolific.com")
ALLOCATION_SEED = os.environ.get("ALLOCATION_SEED", "he-canvas-2026")   # fix before launch; never change after
ALLOCATION_SLOTS = int(os.environ.get("ALLOCATION_SLOTS", "2000"))
ALLOW_FORCED_CONDITION = os.environ.get("ALLOW_FORCED_CONDITION", "") == "1"   # testing only
ALLOW_PREVIEW_PID = os.environ.get("ALLOW_PREVIEW_PID", "") == "1"             # testing only
CANVAS_SECONDS = int(os.environ.get("CANVAS_SECONDS", "1200"))
ASSIGNED_IDEA = int(os.environ.get("ASSIGNED_IDEA", str(content.DEFAULT_ASSIGNED_IDEA)))
SURVEY_URL = os.environ.get("SURVEY_URL", "")
UI_MODE = os.environ.get("UI_MODE", "canvas")      # "canvas" (nine boxes in order), "machine" (one animated screen) or "pitch" (challenge framing + mini-videos)
MACHINE = UI_MODE in ("machine", "shop")          # one animated screen (the shop is the machine screen on a map)
SHOP = UI_MODE == "shop"
PITCH = UI_MODE in ("pitch", "shop")     # "pitch": the canvas framed as a pitch challenge, with short animated mini-videos
TEXTS = content.texts(UI_MODE)
MAX_USER_MESSAGES = int(os.environ.get("MAX_USER_MESSAGES", "60"))
MAX_MESSAGE_CHARS = int(os.environ.get("MAX_MESSAGE_CHARS", "1500"))
MAX_QUICK_REPLIES = int(os.environ.get("MAX_QUICK_REPLIES", "150"))      # tapped chips and helper buttons
PID_RE = re.compile(r"^[A-Za-z0-9_\-]{1,64}$")
AI_CONDITIONS = {"canvas_ai"}

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 256 * 1024

SCHEMA = """
CREATE TABLE IF NOT EXISTS participants (
    pid TEXT PRIMARY KEY, condition TEXT NOT NULL, idea_index INTEGER NOT NULL,
    first_seen REAL NOT NULL, last_seen REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS allocation (
    slot INTEGER PRIMARY KEY, block INTEGER NOT NULL, condition TEXT NOT NULL, pid TEXT UNIQUE, assigned_at REAL
);
CREATE TABLE IF NOT EXISTS canvas (
    pid TEXT PRIMARY KEY, boxes_json TEXT NOT NULL, started_at REAL, updated_at REAL NOT NULL,
    submitted_at REAL, how_submitted TEXT, complete INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS canvas_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT, pid TEXT NOT NULL, box TEXT NOT NULL, text TEXT NOT NULL, created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT, pid TEXT NOT NULL, role TEXT NOT NULL, content TEXT NOT NULL,
    model TEXT, created_at REAL NOT NULL, box TEXT, suggestions TEXT, kind TEXT
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT, pid TEXT NOT NULL, page TEXT, event_type TEXT NOT NULL, detail TEXT,
    created_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_messages_pid ON messages (pid, id);
CREATE INDEX IF NOT EXISTS idx_log_pid ON canvas_log (pid, id);
CREATE INDEX IF NOT EXISTS idx_events_pid ON events (pid, id);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH, timeout=30)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA journal_mode=WAL")
        g.db.execute("PRAGMA busy_timeout=30000")
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH, timeout=30)
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    cols = {r[1] for r in db.execute("PRAGMA table_info(messages)")}
    for col in ("box", "suggestions", "kind"):        # upgrade databases created before these columns existed
        if col not in cols:
            db.execute(f"ALTER TABLE messages ADD COLUMN {col} TEXT")
    if "own_idea" not in {r[1] for r in db.execute("PRAGMA table_info(participants)")}:
        db.execute("ALTER TABLE participants ADD COLUMN own_idea TEXT")
    randomisation.ensure_sequence(db, ALLOCATION_SEED, ALLOCATION_SLOTS)
    db.commit()
    db.close()


init_db()


@app.after_request
def security_headers(resp):
    resp.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; "
        f"frame-ancestors {FRAME_ANCESTORS}")
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["Referrer-Policy"] = "no-referrer"
    resp.headers["X-Content-Type-Options"] = "nosniff"
    return resp


def valid_pid(pid):
    return isinstance(pid, str) and bool(PID_RE.match(pid))


def json_body():
    return request.get_json(silent=True) or {}


def log_event(db, pid, page, event_type, detail=None):
    db.execute("INSERT INTO events (pid, page, event_type, detail, created_at) VALUES (?, ?, ?, ?, ?)",
               (pid, page, event_type, None if detail is None else str(detail)[:500], time.time()))


def participant(db, pid):
    if not valid_pid(pid):
        return None
    return db.execute("SELECT * FROM participants WHERE pid = ?", (pid,)).fetchone()


# Wording of the challenge award on the start page. Set CHALLENGE_AWARD / CHALLENGE_AWARD_SHORT to the real
# award and judging rule; the defaults promise nothing concrete.
AWARD_TEXT = os.environ.get("CHALLENGE_AWARD", "Project plans will be evaluated by researchers in entrepreneurship. The strongest project plan will be awarded double the rate.")
AWARD_SHORT = os.environ.get("CHALLENGE_AWARD_SHORT", "Strongest plan: double the rate")
OWN_IDEA_MAX_CHARS = 400
OWN_IDEA_MIN_WORDS = 1      # no word limit: any idea text is accepted, only an empty box is not


def clean_own_idea(raw):
    """The participant's own idea: one block of text, whitespace collapsed, limited length."""
    return " ".join(str(raw or "").split())[:OWN_IDEA_MAX_CHARS]


def idea_of(row):
    """The idea the participant works on: their own idea in their own words (the five ideas are examples only)."""
    own = (row["own_idea"] or "").strip() if "own_idea" in row.keys() else ""
    if own:
        name = own if len(own) <= 70 else own[:67].rsplit(" ", 1)[0] + "..."
        return {"name": name, "what": own, "line": own, "own": True}
    return content.IDEAS[row["idea_index"] - 1]


def word_count(text):
    return len(text.split())


def clean_boxes(raw):
    """Keep only known keys, as trimmed strings of limited length."""
    raw = raw if isinstance(raw, dict) else {}
    out = {"title": str(raw.get("title") or "")[:80], "tagline": str(raw.get("tagline") or "")[:140],
           "theme": raw.get("theme") if raw.get("theme") in content.THEME_KEYS else content.THEME_KEYS[0]}
    for k in content.BLOCK_KEYS:
        out[k] = str(raw.get(k) or "")[:content.MAX_BOX_CHARS]
    return out


def filled_count(boxes):
    return sum(1 for k in content.BLOCK_KEYS if boxes.get(k, "").strip())


def load_boxes(db, pid):
    row = db.execute("SELECT boxes_json FROM canvas WHERE pid = ?", (pid,)).fetchone()
    return clean_boxes(json.loads(row["boxes_json"])) if row else clean_boxes({})


# ---------------------------------------------------------------------------
# Participant pages
# ---------------------------------------------------------------------------

@app.route("/health")
def health():
    return jsonify(status="ok", ai=llm.provider())


@app.route("/")
def index():
    return redirect(url_for("study", **request.args))


@app.route("/study")
def study():
    pid = (request.args.get("pid") or request.args.get("PROLIFIC_PID") or "").strip()
    if not pid and ALLOW_PREVIEW_PID:
        pid = "PREVIEW-" + secrets.token_hex(4)
    if not valid_pid(pid):
        return render_template("message.html", text="This link is missing your participant ID. "
                               "Please open the study again from Prolific."), 400
    db = get_db()
    row = participant(db, pid)
    now = time.time()
    if row is None:
        forced = request.args.get("cond", "")
        if ALLOW_FORCED_CONDITION and forced in randomisation.CONDITIONS:
            condition = forced
        else:
            condition, _slot = randomisation.assign(db, pid)
        idea_index = ASSIGNED_IDEA if 1 <= ASSIGNED_IDEA <= len(content.IDEAS) else content.DEFAULT_ASSIGNED_IDEA
        db.execute("INSERT OR IGNORE INTO participants (pid, condition, idea_index, first_seen, last_seen) "
                   "VALUES (?, ?, ?, ?, ?)", (pid, condition, idea_index, now, now))
        log_event(db, pid, "study", "registered", condition)
    else:
        db.execute("UPDATE participants SET last_seen = ? WHERE pid = ?", (now, pid))
    db.commit()
    return redirect(url_for("intro", pid=pid))


@app.route("/admin/try/<which>")
def admin_try(which):
    """Permanent researcher link: every visit starts a fresh PREVIEW-... participant in the chosen group.
    Works even when ALLOW_FORCED_CONDITION=0, and only with the admin token."""
    if not admin_ok():
        abort(403)
    if which not in ("ai", "noai"):
        abort(404)
    pid = "PREVIEW-" + which.upper() + "-" + secrets.token_hex(3)
    now = time.time()
    db = get_db()
    condition = "canvas_ai" if which == "ai" else "canvas_noai"
    db.execute("INSERT INTO participants (pid, condition, idea_index, first_seen, last_seen) VALUES (?, ?, ?, ?, ?)",
               (pid, condition, ASSIGNED_IDEA if 1 <= ASSIGNED_IDEA <= len(content.IDEAS) else content.DEFAULT_ASSIGNED_IDEA, now, now))
    log_event(db, pid, "study", "registered", condition + " (researcher preview)")
    db.commit()
    return redirect(url_for("intro", pid=pid))


def js_texts(ai):
    """Only the texts the browser script needs (the no-AI page must not carry any AI wording)."""
    keys = ["saved", "need_more", "confirm_title", "confirm_text", "confirm_yes", "confirm_no", "timeup",
            "progress", "locked", "empty_box", "editor_hint", "done_next", "done_last", "unlocked", "close",
            "preview_title", "guide_think", "guide_example", "hybrid_label", "all_done"]
    if ai:
        keys += ["ai_error", "ai_thinking", "ai_for_box", "ai_use", "ai_used", "ai_quick_more", "ai_quick_start", "ai_quick_feedback",
                 "ai_back_to", "ai_new"]
    if MACHINE:
        keys += [k for k in content.MACHINE_TEXT if k.startswith("m_")]
    if PITCH:
        keys += [k for k in content.PITCH_TEXT if k.startswith("v_")]
    return {k: TEXTS[k] for k in keys}


def page_context(db, pid):
    row = participant(db, pid)
    if row is None:
        return None
    idea = idea_of(row)
    return {"pid": pid, "ai": row["condition"] in AI_CONDITIONS, "idea": idea, "idea_n": row["idea_index"],
            "own_idea": (row["own_idea"] or "") if "own_idea" in row.keys() else "", "idea_max": OWN_IDEA_MAX_CHARS,
            "idea_min_words": OWN_IDEA_MIN_WORDS, "ideas": content.IDEAS, "t": TEXTS, "js_t": js_texts(row["condition"] in AI_CONDITIONS), "blocks": content.BLOCKS, "award": AWARD_TEXT, "award_short": AWARD_SHORT, "minutes": CANVAS_SECONDS // 60,
            "min_filled": content.MIN_FILLED_BOXES, "themes": content.THEMES, "example_business": content.EXAMPLE_BUSINESS,
            "min_words": content.MIN_WORDS_TO_UNLOCK, "pitch": PITCH, "shop": SHOP, "videos": content.VIDEOS if PITCH else {}}


@app.route("/api/idea", methods=["POST"])
def api_idea():
    """The participant enters the idea they want to develop, in their own words (only before any box is filled)."""
    body = request.get_json(silent=True) or {}
    pid = str(body.get("pid", ""))[:100]
    text = clean_own_idea(body.get("text"))
    if len(text.split()) < OWN_IDEA_MIN_WORDS:
        return jsonify(error="too_short", min_words=OWN_IDEA_MIN_WORDS), 400
    db = get_db()
    row = participant(db, pid)
    if row is None:
        return jsonify(error="bad request"), 400
    c = db.execute("SELECT boxes_json FROM canvas WHERE pid = ?", (pid,)).fetchone()
    started = False
    if c and c["boxes_json"]:
        try:
            started = any(str(v).strip() for k, v in json.loads(c["boxes_json"]).items() if k in content.BLOCK_BY_KEY)
        except ValueError:
            pass
    if started:
        return jsonify(ok=False, idea=row["own_idea"] or "")
    db.execute("UPDATE participants SET own_idea = ? WHERE pid = ?", (text, pid))
    log_event(db, pid, "intro", "idea_entered", len(text.split()))
    db.commit()
    return jsonify(ok=True, idea=text)


@app.route("/intro")
def intro():
    db = get_db()
    ctx = page_context(db, request.args.get("pid", ""))
    if ctx is None:
        return redirect(url_for("study", **request.args))
    log_event(db, ctx["pid"], "intro", "page_view")
    db.commit()
    return render_template("intro.html", chosen=bool(ctx["own_idea"]), **ctx)


def chat_history(db, pid):
    """The stored conversation, ready for the page: role, text, suggestions, box, kind."""
    out = []
    for r in db.execute("SELECT role, content, box, suggestions, kind FROM messages WHERE pid = ? ORDER BY id", (pid,)):
        block = content.BLOCK_BY_KEY.get(r["box"] or "")
        out.append({"role": r["role"], "content": r["content"], "box": r["box"], "kind": r["kind"] or "",
                    "box_title": block["title"] if block else "",
                    "suggestions": json.loads(r["suggestions"]) if r["suggestions"] else []})
    return out


def llm_history(db, pid):
    """The conversation as the AI should see it: suggestions it gave are written out in its own turns."""
    out = []
    for m in chat_history(db, pid):
        text = m["content"]
        if m["role"] == "assistant" and m["suggestions"]:
            text += "\nMy suggestions: " + " | ".join(m["suggestions"])
        if m["role"] == "assistant" and m["kind"] in ("auto", "reopen") and m["box_title"]:
            text = f'[I opened the box "{m["box_title"]}" and said:] ' + text
        out.append({"role": m["role"], "content": text})
    return out


@app.route("/canvas")
def canvas_page():
    db = get_db()
    ctx = page_context(db, request.args.get("pid", ""))
    if ctx is None:
        return redirect(url_for("study", **request.args))
    pid = ctx["pid"]
    if not ctx["own_idea"]:                 # the participant has not entered an idea yet: back to the start page
        return redirect(url_for("intro", pid=pid))
    saved = db.execute("SELECT * FROM canvas WHERE pid = ?", (pid,)).fetchone()
    late = bool(saved and saved["submitted_at"] and request.args.get("late") and (MACHINE or PITCH))
    if saved and saved["submitted_at"] and not late:
        return redirect(url_for("done", pid=pid))
    now = time.time()
    if saved is None:
        db.execute("INSERT INTO canvas (pid, boxes_json, started_at, updated_at) VALUES (?, ?, ?, ?)",
                   (pid, json.dumps(clean_boxes({})), now, now))
        started = now
    else:
        started = saved["started_at"] or now
    if ctx["ai"] and not db.execute("SELECT 1 FROM messages WHERE pid = ?", (pid,)).fetchone():
        db.execute("INSERT INTO messages (pid, role, content, model, created_at, kind) "
                   "VALUES (?, 'assistant', ?, 'static', ?, 'greeting')",
                   (pid, TEXTS["ai_opening"].replace("{idea}", ctx["idea"]["name"]), now))
    log_event(db, pid, "canvas", "page_view")
    db.commit()
    history = chat_history(db, pid) if ctx["ai"] else []
    ctx.update(boxes=load_boxes(db, pid), history=history, seeded_boxes=[m["box"] for m in history if m["kind"] in ("auto", "reopen")],
               seconds_left=max(0, int(CANVAS_SECONDS - (now - started))), late=late)
    return render_template("machine.html" if MACHINE else "canvas.html", **ctx)


@app.route("/done")
def done():
    db = get_db()
    ctx = page_context(db, request.args.get("pid", ""))
    if ctx is None:
        return redirect(url_for("study", **request.args))
    pid = ctx["pid"]
    saved = db.execute("SELECT submitted_at FROM canvas WHERE pid = ?", (pid,)).fetchone()
    if not saved or not saved["submitted_at"]:        # the survey link is only shown after the slide is handed in
        return redirect(url_for("canvas_page", pid=pid))
    log_event(db, pid, "done", "page_view")
    db.commit()
    survey = ""
    if SURVEY_URL:
        survey = SURVEY_URL + ("&" if "?" in SURVEY_URL else "?") + "pid=" + quote(pid)
    return render_template("done.html", survey_url=survey, condition=participant(db, pid)["condition"], **ctx)


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

def save_canvas(db, pid, boxes, now):
    """Store the current slide and log every box that changed (keeps the full editing history)."""
    old = load_boxes(db, pid)
    for key in ["title", "tagline", "theme"] + content.BLOCK_KEYS:
        if boxes[key] != old.get(key, ""):
            db.execute("INSERT INTO canvas_log (pid, box, text, created_at) VALUES (?, ?, ?, ?)",
                       (pid, key, boxes[key], now))
    db.execute("UPDATE canvas SET boxes_json = ?, updated_at = ? WHERE pid = ?", (json.dumps(boxes), now, pid))


@app.route("/api/canvas", methods=["POST"])
def api_canvas():
    body = json_body()
    pid = body.get("pid")
    db = get_db()
    row = participant(db, pid)
    saved = db.execute("SELECT submitted_at FROM canvas WHERE pid = ?", (pid,)).fetchone() if row else None
    if row is None or saved is None:
        return jsonify(error="unknown participant"), 404
    if saved["submitted_at"]:
        return jsonify(ok=True, submitted=True)
    save_canvas(db, pid, clean_boxes(body.get("boxes")), time.time())
    db.commit()
    return jsonify(ok=True)


@app.route("/api/canvas/submit", methods=["POST"])
def api_canvas_submit():
    """how = 'button' (participant) or 'timeout' (the timer ran out; handed in as it is)."""
    body = json_body()
    pid = body.get("pid")
    how = "timeout" if body.get("how") == "timeout" else "button"
    db = get_db()
    row = participant(db, pid)
    saved = db.execute("SELECT submitted_at FROM canvas WHERE pid = ?", (pid,)).fetchone() if row else None
    if row is None or saved is None:
        return jsonify(error="unknown participant"), 404
    if saved["submitted_at"]:
        return jsonify(ok=True)
    boxes = clean_boxes(body.get("boxes"))
    enough = filled_count(boxes) >= content.MIN_FILLED_BOXES
    if how == "button" and not enough:
        return jsonify(error="need_more", min=content.MIN_FILLED_BOXES), 400
    now = time.time()
    save_canvas(db, pid, boxes, now)
    db.execute("UPDATE canvas SET submitted_at = ?, how_submitted = ?, complete = ? WHERE pid = ?",
               (now, how, 1 if enough else 0, pid))
    log_event(db, pid, "canvas", "submitted", how)
    db.commit()
    return jsonify(ok=True)


def ai_participant(db, pid):
    row = participant(db, pid)
    return row if row is not None and row["condition"] in AI_CONDITIONS else None


def ask_ai(db, row, pid, boxes, box_key, mode):
    """One call to the model. mode: 'open', 'reopen' or 'chat'. Returns (reply, suggestions, model)."""
    prompt = system_prompt(idea_of(row), boxes, box_key, mode, machine=MACHINE or PITCH, pitch=PITCH)
    history = llm_history(db, pid)
    if mode == "brief":
        history.append({"role": "user", "content": "This is my idea. What shapes it, and where should I start?"})
    elif mode == "open":
        history.append({"role": "user", "content": "I just opened this box. What do you suggest?"})
    elif mode == "reopen":
        history.append({"role": "user", "content": "I'm back at this box and I've worked on it. What do you think?"})
    text, model_used = llm.reply(prompt, history)
    reply, suggestions = parse_reply(text)
    if not reply.strip():
        raise RuntimeError("empty reply %s %r" % (llm.LAST, text[:120]))
    return reply, suggestions, model_used


@app.route("/api/suggest", methods=["POST"])
def api_suggest():
    """AI group: the co-founder's suggestions for a box, created the first time the participant opens it."""
    body = json_body()
    pid, box_key = body.get("pid"), body.get("box")
    db = get_db()
    row = ai_participant(db, pid)
    if row is None:
        return jsonify(error="no AI for this participant"), 403
    if box_key not in content.BLOCK_BY_KEY:
        return jsonify(error="unknown box"), 400
    refresh = bool(body.get("refresh"))
    stored = db.execute("SELECT content, suggestions FROM messages WHERE pid = ? AND kind = 'auto' AND box = ?",
                        (pid, box_key)).fetchone()
    if stored and not refresh:
        return jsonify(reply=stored["content"], suggestions=json.loads(stored["suggestions"] or "[]"), cached=True)
    if refresh:     # coming back to a changed box: a fresh reaction, at most three times per box
        n = db.execute("SELECT COUNT(*) FROM messages WHERE pid = ? AND kind = 'reopen' AND box = ?",
                       (pid, box_key)).fetchone()[0]
        if n >= 3:
            return jsonify(error="limit"), 429
    kind = "reopen" if refresh else "auto"
    try:
        reply, suggestions, model_used = ask_ai(db, row, pid, clean_boxes(body.get("boxes")), box_key,
                                                "reopen" if refresh else "open")
    except Exception as exc:
        print("AI error:", repr(exc), file=sys.stderr, flush=True)
        log_event(db, pid, "canvas", "ai_error", repr(exc)[:300])
        db.commit()
        return jsonify(error=TEXTS["ai_error"]), 502
    db.execute("INSERT INTO messages (pid, role, content, model, created_at, box, suggestions, kind) "
               "VALUES (?, 'assistant', ?, ?, ?, ?, ?, ?)",
               (pid, reply, model_used, time.time(), box_key, json.dumps(suggestions), kind))
    db.commit()
    return jsonify(reply=reply, suggestions=suggestions)


@app.route("/api/brief", methods=["POST"])
def api_brief():
    """AI group: Compi's short opening about the participant's own idea (what shapes it), created once when the map opens."""
    body = json_body()
    pid = body.get("pid")
    db = get_db()
    row = ai_participant(db, pid)
    if row is None:
        return jsonify(error="no AI for this participant"), 403
    stored = db.execute("SELECT content, suggestions FROM messages WHERE pid = ? AND kind = 'brief'", (pid,)).fetchone()
    if stored:
        return jsonify(reply=stored["content"], suggestions=json.loads(stored["suggestions"] or "[]"), cached=True)
    try:
        reply, suggestions, model_used = ask_ai(db, row, pid, clean_boxes(body.get("boxes")), None, "brief")
    except Exception as exc:
        print("AI error:", repr(exc), file=sys.stderr, flush=True)
        log_event(db, pid, "canvas", "ai_error", repr(exc)[:300])
        db.commit()
        return jsonify(error=TEXTS["ai_error"]), 502
    db.execute("INSERT INTO messages (pid, role, content, model, created_at, box, suggestions, kind) "
               "VALUES (?, 'assistant', ?, ?, ?, NULL, ?, 'brief')", (pid, reply, model_used, time.time(), json.dumps(suggestions)))
    db.commit()
    return jsonify(reply=reply, suggestions=suggestions)


@app.route("/api/chat", methods=["POST"])
def api_chat():
    body = json_body()
    pid, box_key = body.get("pid"), body.get("box")
    db = get_db()
    row = ai_participant(db, pid)
    if row is None:
        return jsonify(error="no AI for this participant"), 403
    text = str(body.get("message") or "").strip()
    if not text:
        return jsonify(error="empty message"), 400
    if box_key not in content.BLOCK_BY_KEY:
        box_key = content.BLOCKS[0]["key"]
    text = text[:MAX_MESSAGE_CHARS]
    quick = body.get("quick") in ("more", "start", "feedback", "choice")     # helper buttons and tapped answer chips are not typed prompts
    if quick:
        n_quick = db.execute("SELECT COUNT(*) FROM messages WHERE pid = ? AND kind = 'quick'", (pid,)).fetchone()[0]
        if n_quick >= MAX_QUICK_REPLIES:
            return jsonify(error="message limit reached"), 429
    if not quick:
        n_user = db.execute("SELECT COUNT(*) FROM messages WHERE pid = ? AND role = 'user' "
                            "AND COALESCE(kind, '') != 'quick'", (pid,)).fetchone()[0]
        if n_user >= MAX_USER_MESSAGES:
            return jsonify(error="message limit reached"), 429
    db.execute("INSERT INTO messages (pid, role, content, model, created_at, box, kind) "
               "VALUES (?, 'user', ?, NULL, ?, ?, ?)", (pid, text, time.time(), box_key, "quick" if quick else "reply"))
    db.commit()
    try:
        reply, suggestions, model_used = ask_ai(db, row, pid, clean_boxes(body.get("boxes")), box_key, "chat")
    except Exception as exc:
        print("AI error:", repr(exc), file=sys.stderr, flush=True)
        log_event(db, pid, "canvas", "ai_error", repr(exc)[:300])
        db.commit()
        return jsonify(error=TEXTS["ai_error"]), 502
    db.execute("INSERT INTO messages (pid, role, content, model, created_at, box, suggestions, kind) "
               "VALUES (?, 'assistant', ?, ?, ?, ?, ?, 'reply')",
               (pid, reply, model_used, time.time(), box_key, json.dumps(suggestions)))
    db.commit()
    return jsonify(reply=reply, suggestions=suggestions)


@app.route("/api/interest", methods=["POST"])
def api_interest():
    """Machine mode: how much the participant wants the prototype (1-7) and whether they would take it. No money involved."""
    body = json_body()
    pid = body.get("pid")
    db = get_db()
    if participant(db, pid) is None:
        return jsonify(error="unknown participant"), 404
    try:
        rating = int(body.get("rating"))
    except (TypeError, ValueError):
        return jsonify(error="bad rating"), 400
    if not 1 <= rating <= 7 or not isinstance(body.get("take"), bool):
        return jsonify(error="bad answer"), 400
    log_event(db, pid, "machine", "interest", json.dumps({"rating": rating, "take": body["take"]}))
    db.commit()
    return jsonify(ok=True)


@app.route("/api/event", methods=["POST"])
def api_event():
    body = json_body()
    pid = body.get("pid")
    db = get_db()
    if participant(db, pid) is None:
        return jsonify(error="unknown participant"), 404
    events = body.get("events") if isinstance(body.get("events"), list) else [body]
    for e in events[:50]:
        if isinstance(e, dict) and re.match(r"^[a-z_]{1,40}$", str(e.get("type", ""))):
            log_event(db, pid, str(e.get("page", ""))[:20], e["type"], e.get("detail"))
    db.commit()
    return jsonify(ok=True)


# ---------------------------------------------------------------------------
# Researcher exports (token protected)
# ---------------------------------------------------------------------------

def admin_ok():
    token = request.args.get("token", "") or request.headers.get("X-Admin-Token", "")
    return bool(ADMIN_TOKEN) and hmac.compare_digest(token, ADMIN_TOKEN)


EXPORTS = {
    "summary": """
        SELECT p.pid, p.condition, p.idea_index, p.own_idea, datetime(p.first_seen, 'unixepoch') AS first_seen,
               c.complete, c.how_submitted,
               ROUND(c.submitted_at - c.started_at, 1) AS seconds_on_canvas,
               (SELECT COUNT(*) FROM messages m WHERE m.pid = p.pid AND m.role = 'user'
                  AND COALESCE(m.kind, '') != 'quick') AS n_user_messages,
               (SELECT COUNT(*) FROM messages m WHERE m.pid = p.pid AND m.kind = 'quick') AS n_quick_buttons,
               (SELECT COUNT(*) FROM messages m WHERE m.pid = p.pid AND m.kind = 'auto') AS n_suggestion_sets,
               (SELECT COUNT(*) FROM messages m WHERE m.pid = p.pid AND m.kind = 'reopen') AS n_reopen_sets,
               (SELECT COUNT(*) FROM events e WHERE e.pid = p.pid AND e.event_type = 'suggestion_used') AS n_suggestions_used,
               (SELECT COUNT(*) FROM events e WHERE e.pid = p.pid AND e.event_type = 'box_opened') AS n_box_opens,
               COALESCE((SELECT SUM(LENGTH(TRIM(m.content)) - LENGTH(REPLACE(TRIM(m.content), ' ', '')) + 1)
                         FROM messages m WHERE m.pid = p.pid AND m.role = 'user'
                         AND COALESCE(m.kind, '') != 'quick'), 0) AS prompt_words_total,
               (SELECT COUNT(*) FROM canvas_log l WHERE l.pid = p.pid) AS n_edits,
               (SELECT json_extract(e.detail, '$.rating') FROM events e WHERE e.pid = p.pid AND e.event_type = 'interest' ORDER BY e.id DESC LIMIT 1) AS interest_rating,
               (SELECT json_extract(e.detail, '$.take') FROM events e WHERE e.pid = p.pid AND e.event_type = 'interest' ORDER BY e.id DESC LIMIT 1) AS interest_take,
               (SELECT COUNT(*) FROM events e WHERE e.pid = p.pid AND e.event_type = 'machine_started') AS n_machine_starts,
               c.boxes_json
        FROM participants p LEFT JOIN canvas c ON c.pid = p.pid ORDER BY p.first_seen""",
    "participants": "SELECT * FROM participants ORDER BY first_seen",
    "canvas_log": "SELECT * FROM canvas_log ORDER BY id",
    "messages": "SELECT * FROM messages ORDER BY id",
    "events": "SELECT * FROM events ORDER BY id",
    "allocation": "SELECT * FROM allocation WHERE pid IS NOT NULL ORDER BY slot",
}


def rows_to_csv(rows, columns):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(columns)
    for r in rows:
        w.writerow([safe_cell(r[c]) for c in columns])
    return buf.getvalue()


def safe_cell(value):
    """Participant text that starts with = + - @ would run as a formula when the CSV is opened in Excel."""
    if isinstance(value, str) and value[:1] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + value
    return value


@app.route("/admin/export/<name>.csv")
def admin_export(name):
    if not admin_ok():
        abort(403)
    if name == "canvases":      # one row per participant, one column per box
        db = get_db()
        rows = db.execute("SELECT p.pid, p.condition, c.complete, c.how_submitted, c.boxes_json FROM participants p "
                          "JOIN canvas c ON c.pid = p.pid ORDER BY p.first_seen").fetchall()
        cols = ["pid", "condition", "complete", "how_submitted", "title", "tagline", "theme"] + content.BLOCK_KEYS
        out = []
        for r in rows:
            boxes = clean_boxes(json.loads(r["boxes_json"]))
            out.append({"pid": r["pid"], "condition": r["condition"], "complete": r["complete"],
                        "how_submitted": r["how_submitted"], **{k: boxes[k] for k in ["title", "tagline", "theme"] + content.BLOCK_KEYS}})
        return Response(rows_to_csv(out, cols), mimetype="text/csv",
                        headers={"Content-Disposition": "attachment; filename=canvases.csv"})
    sql = EXPORTS.get(name)
    if sql is None:
        abort(404)
    cur = get_db().execute(sql)
    cols = [d[0] for d in cur.description]
    return Response(rows_to_csv(cur.fetchall(), cols), mimetype="text/csv",
                    headers={"Content-Disposition": f"attachment; filename={name}.csv"})


@app.route("/plan")
def plan_download():
    """The participant's own project plan as a standalone page they can keep (opens in any browser, print -> PDF)."""
    db = get_db()
    pid = request.args.get("pid", "")
    row = participant(db, pid) if pid else None
    if row is None:
        abort(404)
    boxes = load_boxes(db, pid)
    log_event(db, pid, "plan", "download")
    db.commit()
    html = render_template("plan.html", idea=idea_of(row), boxes=boxes, blocks=content.BLOCKS)
    name = re.sub(r"[^a-z0-9]+", "-", (boxes.get("title") or "my-project").lower()).strip("-")[:28] or "my-project"
    return Response(html, mimetype="text/html",
                    headers={"Content-Disposition": f'attachment; filename="{name}-project-plan.html"'})


@app.route("/admin/slide/<pid>")
def admin_slide(pid):
    """The participant's slide as a printable page (browser: Print -> Save as PDF)."""
    if not admin_ok():
        abort(403)
    db = get_db()
    row = participant(db, pid)
    if row is None:
        abort(404)
    return render_template("slide.html", pid=pid, condition=row["condition"], idea=idea_of(row),
                           boxes=load_boxes(db, pid), blocks=content.BLOCKS, t=TEXTS,
                           color=next(t["color"] for t in content.THEMES if t["key"] == load_boxes(db, pid)["theme"]))


@app.route("/admin/balance")
def admin_balance():
    if not admin_ok():
        abort(403)
    rows = get_db().execute("SELECT condition, COUNT(*) AS n FROM participants GROUP BY condition").fetchall()
    return jsonify({r["condition"]: r["n"] for r in rows})


@app.route("/admin/llmtest")
def admin_llmtest():
    """Open /admin/llmtest?token=... to see which provider and model are live and how long one call takes."""
    if not admin_ok():
        abort(403)
    if request.args.get("deep"):                    # ?deep=1: one real opening brief, with the raw model output
        t0 = time.time()
        try:
            idea = {"name": "Dog walking", "what": "Dog walking for busy students in Leeds", "line": "", "own": True}
            text, model = llm.reply(system_prompt(idea, clean_boxes({}), None, "brief", machine=MACHINE or PITCH, pitch=PITCH),
                                    [{"role": "user", "content": "This is my idea. What shapes it, and where should I start?"}])
            reply_text, sugg = parse_reply(text)
            return jsonify(raw=text, parsed=reply_text, suggestions=sugg, last=llm.LAST, seconds=round(time.time() - t0, 2))
        except Exception as exc:
            return jsonify(error=repr(exc), last=llm.LAST, seconds=round(time.time() - t0, 2)), 500
    t0 = time.time()
    try:
        text, model = llm.reply("You are a test. Answer in one word.", [{"role": "user", "content": "Say OK."}])
        return jsonify(provider=llm.provider(), model=model, reply=text, seconds=round(time.time() - t0, 2),
                       timeout=llm.LLM_TIMEOUT, max_tokens=llm.MAX_OUTPUT_TOKENS, thinking=llm.ANTHROPIC_THINKING or "disabled")
    except Exception as exc:
        return jsonify(provider=llm.provider(), model=llm.model_name(), error=repr(exc),
                       seconds=round(time.time() - t0, 2)), 500


@app.errorhandler(413)
def too_big(_err):
    return jsonify(error="too large"), 413


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
