import csv, io, json, os, tempfile
os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "t.db")
os.environ["ADMIN_TOKEN"] = "tok"
os.environ["ALLOW_FORCED_CONDITION"] = "1"
os.environ["ALLOW_PREVIEW_PID"] = "1"
os.environ["SURVEY_URL"] = "https://example.qualtrics.com/jfe/form/SV_x"
for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "AZURE_OPENAI_API_KEY"):
    os.environ.pop(k, None)
import app as study, content, randomisation

c = study.app.test_client()


def start(pid, cond=None):
    q = f"/study?pid={pid}" + (f"&cond={cond}" if cond else "")
    r = c.get(q)
    assert r.status_code == 302 and "/intro" in r.headers["Location"], r.status_code
    return r


def test_balance_and_same_ideas():
    for i in range(16):
        start(f"P{i:03d}")
    with study.app.app_context():
        rows = study.get_db().execute("SELECT condition, COUNT(*) n FROM participants GROUP BY condition").fetchall()
    counts = {r["condition"]: r["n"] for r in rows}
    assert counts == {"canvas_ai": 8, "canvas_noai": 8}, counts
    # intro page: all five ideas, the same for both conditions, the assigned one marked
    pages = {}
    for pid, cond in (("A1", "canvas_ai"), ("N1", "canvas_noai")):
        start(pid, cond)
        pages[cond] = c.get(f"/intro?pid={pid}").get_data(as_text=True)
    for cond, page in pages.items():
        for i in content.IDEAS:
            assert i["name"] in page
        assert page.count("idea-chosen") == 1
    assert "AI co-founder" in pages["canvas_ai"] and "on your own" in pages["canvas_noai"]


def test_canvas_pages():
    start("A2", "canvas_ai"); start("N2", "canvas_noai")
    ai, noai = (c.get(f"/canvas?pid={p}").get_data(as_text=True) for p in ("A2", "N2"))
    assert 'id="chatform"' in ai and "Hi, I&#39;m your AI co-founder" in ai.replace("&#39;", "&#39;")
    assert 'id="chatform"' not in noai and "AI co-founder" not in noai
    for b in content.BLOCKS:
        assert b["title"] in ai and b["title"] in noai
    assert c.post("/api/chat", json={"pid": "N2", "message": "hi"}).status_code == 403


def test_save_submit_and_exports():
    start("S1", "canvas_ai"); c.get("/canvas?pid=S1")
    boxes = {"title": "Tail Waggers", **{k: f"text for {k}" for k in content.BLOCK_KEYS}}
    assert c.post("/api/canvas", json={"pid": "S1", "boxes": boxes}).status_code == 200
    boxes["offer"] = "changed offer"
    c.post("/api/canvas", json={"pid": "S1", "boxes": boxes})
    # too few boxes
    start("S2", "canvas_noai"); c.get("/canvas?pid=S2")
    r = c.post("/api/canvas/submit", json={"pid": "S2", "boxes": {"title": "x", "offer": "a"}, "how": "button"})
    assert r.status_code == 400
    # timeout hands in whatever is there, flagged incomplete
    r = c.post("/api/canvas/submit", json={"pid": "S2", "boxes": {"title": "x", "offer": "a"}, "how": "timeout"})
    assert r.status_code == 200
    r = c.post("/api/canvas/submit", json={"pid": "S1", "boxes": boxes, "how": "button"})
    assert r.status_code == 200
    assert c.get("/canvas?pid=S1").status_code == 302          # already handed in -> done
    assert c.post("/api/canvas", json={"pid": "S1", "boxes": {"title": "late"}}).get_json()["submitted"]
    done = c.get("/done?pid=S1").get_data(as_text=True)
    assert "SV_x?pid=S1" in done
    def exp(name, token="tok"):
        return c.get(f"/admin/export/{name}.csv?token={token}")
    assert exp("canvases", "bad").status_code == 403
    rows = list(csv.DictReader(io.StringIO(exp("canvases").get_data(as_text=True))))
    s1 = [r for r in rows if r["pid"] == "S1"][0]
    assert s1["title"] == "Tail Waggers" and s1["offer"] == "changed offer" and s1["complete"] == "1"
    s2 = [r for r in rows if r["pid"] == "S2"][0]
    assert s2["complete"] == "0" and s2["how_submitted"] == "timeout"
    log = list(csv.DictReader(io.StringIO(exp("canvas_log").get_data(as_text=True))))
    assert [r["text"] for r in log if r["pid"] == "S1" and r["box"] == "offer"] == ["text for offer", "changed offer"]
    summ = list(csv.DictReader(io.StringIO(exp("summary").get_data(as_text=True))))
    assert {"n_user_messages", "prompt_words_total", "n_edits"} <= set(summ[0])
    assert "Tail Waggers" in c.get("/admin/slide/S1?token=tok").get_data(as_text=True)


def test_ai_chat_mock():
    start("C1", "canvas_ai"); c.get("/canvas?pid=C1")
    r = c.post("/api/chat", json={"pid": "C1", "message": "Who are my customers?", "boxes": {"customers": "dog owners"}})
    assert r.status_code == 200 and r.get_json()["reply"]
    with study.app.app_context():
        msgs = study.get_db().execute("SELECT role FROM messages WHERE pid = 'C1' ORDER BY id").fetchall()
    assert [m["role"] for m in msgs] == ["assistant", "user", "assistant"]
    import prompts
    p = prompts.system_prompt(content.IDEAS[3], {"customers": "dog owners", "title": "Tail"})
    assert "Pet sitting" in p and "dog owners" in p and "UK" in p


def test_misc():
    assert c.get("/study").status_code == 302       # preview pid allowed in tests
    assert c.get("/intro?pid=NOPE").status_code == 302
    assert c.get("/health").get_json()["status"] == "ok"
    assert c.get("/admin/balance").status_code == 403


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("All canvas tests passed.")
