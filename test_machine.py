# Run on its own: python -m pytest test_machine.py   (machine mode is chosen at start-up with UI_MODE=machine)
import csv, io, os, re, tempfile
os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "t.db")
os.environ.update(ADMIN_TOKEN="tok", ALLOW_FORCED_CONDITION="1", UI_MODE="machine", SURVEY_URL="")
for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "AZURE_OPENAI_API_KEY"):
    os.environ.pop(k, None)
import app as study, content, prompts

c = study.app.test_client()


def test_machine_pages_and_wtp():
    for pid, cond in (("MA", "canvas_ai"), ("MN", "canvas_noai")):
        assert c.get(f"/study?pid={pid}&cond={cond}").status_code == 302
        assert c.post("/api/idea", json={"pid": pid, "text": "Mobile bike repairs for commuters"}).get_json()["ok"]
        intro = c.get(f"/intro?pid={pid}").get_data(as_text=True)
        assert "Turn your idea into a winning project plan" in intro
        page = c.get(f"/canvas?pid={pid}").get_data(as_text=True)
        assert "machine.js" in page and 'id="pods"' in page and "Start the machine" in page
        assert ("AI co-founder" in page) == (cond == "canvas_ai")
        assert ("Compi" in page) == (cond == "canvas_ai")                 # the no-AI page carries no AI wording at all
        assert ("co-founder" in page.lower() or "ai_error" in page) == (cond == "canvas_ai")
    boxes = {"title": "Midday Paws", **{k: f"text for {k}" for k in content.BLOCK_KEYS}}
    assert c.post("/api/canvas/submit", json={"pid": "MA", "boxes": boxes, "how": "button"}).status_code == 200
    assert c.post("/api/interest", json={"pid": "MA", "rating": 6, "take": True}).status_code == 200
    assert c.post("/api/interest", json={"pid": "MA", "rating": 9, "take": True}).status_code == 400
    assert c.post("/api/interest", json={"pid": "MA", "rating": 3}).status_code == 400
    assert c.post("/api/interest", json={"pid": "NOPE", "rating": 3, "take": False}).status_code == 404
    assert c.post("/api/interest", json={"pid": "MN", "rating": 2, "take": False}).status_code == 200
    assert c.post("/api/wtp", json={"pid": "MA", "value": 5}).status_code == 404       # no price question any more
    rows = list(csv.DictReader(io.StringIO(c.get("/admin/export/summary.csv?token=tok").get_data(as_text=True))))
    by = {r["pid"]: r for r in rows}
    assert (by["MA"]["interest_rating"], by["MA"]["interest_take"]) == ("6", "1")
    assert (by["MN"]["interest_rating"], by["MN"]["interest_take"]) == ("2", "0")


def test_ai_prompt_has_automation_note_only_in_machine_mode():
    idea = content.IDEAS[0]
    sim = prompts.system_prompt(idea, {}, "problem", "open", machine=True)
    assert "You are Compi" in sim and "AT MOST 22 words" in sim
    assert "You are Compi" not in prompts.system_prompt(idea, {}, "problem", "open")
    assert c.get("/study?pid=MB&cond=canvas_ai").status_code == 302
    r = c.post("/api/suggest", json={"pid": "MB", "box": "problem", "boxes": {}})
    assert r.status_code == 200 and r.get_json()["reply"]


def test_compi_quick_moves_uk_and_chips():
    own = {"name": "Mobile bike repairs for commuters", "what": "Mobile bike repairs for commuters", "own": True}
    sim = prompts.system_prompt(own, {"problem": "Bikes break at the worst moment"}, "customers", "open", machine=True)
    assert "OWN idea" in sim and "UK CONTEXT" in sim and "Facebook" not in sim and "fits THIS customer" in sim
    assert "5 to 9 words" in sim and "ALWAYS GIVE THE REASON" in sim and "bare example" in sim and "1 of 9 parts have text" in sim and "Which area: big city" in sim
    assert "never with the words" not in sim or "my guess" in sim            # estimates are written as roughly or about, not as a guess
    assert "a guess must be called a guess" not in sim
    assert "Mobile bike repairs for commuters" in sim
    chat = prompts.system_prompt(own, {}, "customers", "chat", machine=True)
    assert "tapped one of your chips" in chat
    assert "first ideas" in chat and "DIFFERENT starting points" in chat
    # greeting carries the participant's idea; tapped chips are quick replies, capped separately from typed messages
    assert c.get("/study?pid=MQ&cond=canvas_ai").status_code == 302
    c.post("/api/idea", json={"pid": "MQ", "text": "Mobile bike repairs for commuters"})
    assert "Mobile bike repairs for commuters" in c.get("/canvas?pid=MQ").get_data(as_text=True)
    r = c.post("/api/chat", json={"pid": "MQ", "message": "Group walks first", "box": "problem", "boxes": {}, "quick": "choice"})
    assert r.status_code == 200 and r.get_json()["reply"]
    r2 = c.post("/api/chat", json={"pid": "MQ", "message": "Give me first ideas", "box": "problem", "boxes": {}, "quick": "start"})
    assert r2.status_code == 200 and r2.get_json()["reply"]
    with study.app.app_context():
        kinds = [x["kind"] for x in study.get_db().execute("SELECT kind FROM messages WHERE pid = 'MQ' AND role = 'user'")]
        assert kinds == ["quick", "quick"]


def test_opening_brief():
    tutor = {"name": "Tutoring", "what": "Tutoring for GCSE maths students", "own": True}
    p = prompts.system_prompt(tutor, {}, None, "brief", machine=True)
    assert "Lean Canvas" in p and "Start with" in p and "exact map title" in p and "never reuse the content" in p and "55 words" in p and "UK" in p
    assert "Who pays" in p and "Money in" in p                              # the nine map parts are listed for the model to choose from
    assert c.get("/study?pid=BR&cond=canvas_ai").status_code == 302
    c.post("/api/idea", json={"pid": "BR", "text": "Tutoring for GCSE maths students"})
    r = c.post("/api/brief", json={"pid": "BR", "boxes": {}}).get_json()
    assert r["reply"] and not r.get("cached")
    again = c.post("/api/brief", json={"pid": "BR", "boxes": {}}).get_json()
    assert again["cached"] and again["reply"] == r["reply"]               # made once, then remembered
    with study.app.app_context():
        assert study.get_db().execute("SELECT COUNT(*) FROM messages WHERE pid='BR' AND kind='brief'").fetchone()[0] == 1
    assert c.get("/study?pid=BN&cond=canvas_noai").status_code == 302
    assert c.post("/api/brief", json={"pid": "BN", "boxes": {}}).status_code == 403    # the no-AI group never gets one


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("All machine tests passed.")


def test_setup_button_only_after_handin_and_separate_counts():
    assert c.get("/study?pid=SU&cond=canvas_ai").status_code == 302
    c.post("/api/idea", json={"pid": "SU", "text": "Mobile bike repairs for commuters"})
    assert "data-quick=\"setup\"" not in c.get("/canvas?pid=SU").get_data(as_text=True)
    assert c.post("/api/chat", json={"pid": "SU", "message": "Help me set up my business", "quick": "setup", "box": "problem", "boxes": {}}).status_code == 403
    boxes = {"title": "Bike Fix", **{k: f"text for {k}" for k in content.BLOCK_KEYS}}
    assert c.post("/api/canvas/submit", json={"pid": "SU", "boxes": boxes, "how": "button"}).status_code == 200
    late = c.get("/canvas?pid=SU&late=1").get_data(as_text=True)
    assert 'data-quick="setup"' in late and "Help me set up my business" in late
    r = c.post("/api/chat", json={"pid": "SU", "message": "Help me set up my business", "quick": "setup", "box": "problem", "boxes": boxes})
    assert r.status_code == 200 and r.get_json()["reply"]
    rows = list(csv.DictReader(io.StringIO(c.get("/admin/export/summary.csv?token=tok").get_data(as_text=True))))
    row = [x for x in rows if x["pid"] == "SU"][0]
    assert (row["n_setup_requests"], row["n_user_messages"], row["n_quick_buttons"]) == ("1", "0", "0")
    assert "Help me set up" in prompts.system_prompt({"name": "x", "what": "y"}, {}, "problem", "setup", machine=True)


def test_no_ai_links_page_demo_note_gone_and_clicks_exported():
    for pid, cond in (("LK1", "canvas_noai"), ("LK2", "canvas_ai")):
        assert c.get(f"/study?pid={pid}&cond={cond}").status_code == 302
        c.post("/api/idea", json={"pid": pid, "text": "Mobile bike repairs for commuters"})
        page = c.get(f"/canvas?pid={pid}").get_data(as_text=True)
        notice = re.search(r'<p class="notice">(.*?)</p>', page, re.S).group(1)
        assert "Demo animation" not in notice and "research purposes" in notice                   # demo sentence gone in both groups, the research note stays
    boxes = {"title": "Bike Fix", **{k: f"text for {k}" for k in content.BLOCK_KEYS}}
    for pid in ("LK1", "LK2"):
        c.post("/api/canvas/submit", json={"pid": pid, "boxes": boxes, "how": "button"})
    noai = c.get("/canvas?pid=LK1&late=1").get_data(as_text=True)
    assert 'id="links-open"' in noai and "vinted.co.uk" in noai and 'data-link="vinted"' in noai
    ai = c.get("/canvas?pid=LK2&late=1").get_data(as_text=True)
    assert 'id="links-open"' not in ai and 'data-quick="setup"' in ai                             # the AI group gets Compi's help instead
    for t, d in (("links_opened", "button"), ("link_click", "vinted"), ("link_click", "calendly"), ("link_click", "vinted")):
        assert c.post("/api/event", json={"pid": "LK1", "page": "machine", "type": t, "detail": d}).status_code == 200
    rows = list(csv.DictReader(io.StringIO(c.get("/admin/export/summary.csv?token=tok").get_data(as_text=True))))
    row = [x for x in rows if x["pid"] == "LK1"][0]
    assert (row["n_links_opened"], row["n_link_clicks"]) == ("1", "3") and set(row["links_clicked"].split(",")) == {"vinted", "calendly"}
    lc = list(csv.DictReader(io.StringIO(c.get("/admin/export/link_clicks.csv?token=tok").get_data(as_text=True))))
    assert [r["link"] for r in lc if r["pid"] == "LK1" and r["event_type"] == "link_click"] == ["vinted", "calendly", "vinted"]
    assert content.LINKS and all(i["url"].startswith("https://") for g in content.LINKS for i in g["items"])
