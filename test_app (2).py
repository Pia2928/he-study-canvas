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
        assert page.count("pick idea-chosen") == 0       # nothing is pre-selected: the participant chooses
    assert "AI co-founder" in pages["canvas_ai"] and "on your own" in pages["canvas_noai"]


def test_canvas_pages():
    start("A2", "canvas_ai"); start("N2", "canvas_noai")
    ai, noai = (c.get(f"/canvas?pid={p}").get_data(as_text=True) for p in ("A2", "N2"))
    assert 'id="chatform"' in ai and "AI co-founder is ready" in ai
    assert 'id="chatform"' not in noai and "AI co-founder" not in noai and " AI " not in noai and "AI " not in noai.split("<script")[0].replace("MAIN", "")
    assert 'id="guide-tips"' in noai and 'id="guide-tips"' not in ai
    for b in content.BLOCKS:
        assert b["title"] in ai and b["title"] in noai
    assert c.post("/api/chat", json={"pid": "N2", "message": "hi"}).status_code == 403
    assert c.post("/api/suggest", json={"pid": "N2", "box": "customers"}).status_code == 403


def test_save_submit_and_exports():
    start("S1", "canvas_ai"); c.get("/canvas?pid=S1")
    boxes = {"title": "Tail Waggers", "tagline": "Walks you can trust", "theme": "teal",
             **{k: f"text for {k}" for k in content.BLOCK_KEYS}}
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
    assert s1["tagline"] == "Walks you can trust" and s1["theme"] == "teal"
    assert s1["title"] == "Tail Waggers" and s1["offer"] == "changed offer" and s1["complete"] == "1"
    s2 = [r for r in rows if r["pid"] == "S2"][0]
    assert s2["complete"] == "0" and s2["how_submitted"] == "timeout"
    log = list(csv.DictReader(io.StringIO(exp("canvas_log").get_data(as_text=True))))
    assert [r["text"] for r in log if r["pid"] == "S1" and r["box"] == "offer"] == ["text for offer", "changed offer"]
    summ = list(csv.DictReader(io.StringIO(exp("summary").get_data(as_text=True))))
    assert {"n_user_messages", "prompt_words_total", "n_edits"} <= set(summ[0])
    assert "Tail Waggers" in c.get("/admin/slide/S1?token=tok").get_data(as_text=True)


def test_ai_suggest_and_chat_mock():
    start("C1", "canvas_ai"); c.get("/canvas?pid=C1")
    r = c.post("/api/suggest", json={"pid": "C1", "box": "customers", "boxes": {}})
    j = r.get_json()
    assert r.status_code == 200 and j["reply"] and len(j["suggestions"]) == 3
    again = c.post("/api/suggest", json={"pid": "C1", "box": "customers", "boxes": {}}).get_json()
    assert again.get("cached") and again["suggestions"] == j["suggestions"]       # asked only once per box
    assert c.post("/api/suggest", json={"pid": "C1", "box": "nonsense"}).status_code == 400
    for i in range(3):      # coming back to a changed box gives a fresh reaction, at most three times
        r2 = c.post("/api/suggest", json={"pid": "C1", "box": "customers", "refresh": True, "boxes": {"customers": f"v{i}"}})
        assert r2.status_code == 200 and not r2.get_json().get("cached")
    assert c.post("/api/suggest", json={"pid": "C1", "box": "customers", "refresh": True}).status_code == 429
    r = c.post("/api/chat", json={"pid": "C1", "message": "Who are my customers?", "box": "customers",
                                  "boxes": {"customers": "students"}})
    assert r.status_code == 200 and r.get_json()["reply"]
    c.post("/api/chat", json={"pid": "C1", "message": "More suggestions", "box": "customers", "quick": "more"})
    with study.app.app_context():
        rows = study.get_db().execute("SELECT role, kind, box FROM messages WHERE pid = 'C1' ORDER BY id").fetchall()
    assert [(m["role"], m["kind"]) for m in rows] == [("assistant", "greeting"), ("assistant", "auto"),
                                                      ("assistant", "reopen"), ("assistant", "reopen"), ("assistant", "reopen"),
                                                      ("user", "reply"),
                                                      ("assistant", "reply"), ("user", "quick"), ("assistant", "reply")]
    summ = {r["pid"]: r for r in csv.DictReader(io.StringIO(
        c.get("/admin/export/summary.csv?token=tok").get_data(as_text=True)))}["C1"]
    assert summ["n_user_messages"] == "1" and summ["n_quick_buttons"] == "1" and summ["n_suggestion_sets"] == "1"
    import prompts
    p = prompts.system_prompt(content.IDEAS[2], {"customers": "students", "title": "Resale"}, "customers", "open")
    assert "Reselling" in p and "students" in p and "UK" in p and "JSON" in p
    assert prompts.parse_reply('{"reply": "Hi", "suggestions": ["a", "b", "c", "d"]}') == ("Hi", ["a", "b", "c"])
    assert prompts.parse_reply("plain text *here*") == ("plain text here", [])


def test_done_requires_handing_in_and_csv_is_safe():
    start("D1", "canvas_noai"); c.get("/canvas?pid=D1")
    assert c.get("/done?pid=D1").status_code == 302 and "/canvas" in c.get("/done?pid=D1").headers["Location"]
    boxes = {"title": "=HYPERLINK(\"http://x\")", **{k: "ok words here" for k in content.BLOCK_KEYS}}
    c.post("/api/canvas/submit", json={"pid": "D1", "boxes": boxes, "how": "button"})
    assert c.get("/done?pid=D1").status_code == 200
    rows = list(csv.DictReader(io.StringIO(c.get("/admin/export/canvases.csv?token=tok").get_data(as_text=True))))
    assert [r for r in rows if r["pid"] == "D1"][0]["title"].startswith("'=")


def test_bad_input_is_handled():
    start("F1", "canvas_ai"); c.get("/canvas?pid=F1")
    assert c.post("/api/canvas", json={"pid": "F1", "boxes": "not a dict"}).status_code == 200
    assert c.post("/api/canvas", data="not json", content_type="text/plain").status_code == 404
    assert c.post("/api/canvas", json={"pid": "../etc", "boxes": {}}).status_code == 404
    assert c.post("/api/chat", json={"pid": "F1", "message": "   "}).status_code == 400
    assert c.post("/api/event", json={"pid": "F1", "events": [{"type": "BAD TYPE!"}, 5, {"type": "paste"}]}).status_code == 200
    big = c.post("/api/canvas", json={"pid": "F1", "boxes": {"customers": "x" * 100000}})
    assert big.status_code == 200
    with study.app.app_context():
        assert len(study.load_boxes(study.get_db(), "F1")["customers"]) == content.MAX_BOX_CHARS
    assert c.get("/study?pid=bad%20id").status_code == 400
    assert c.get("/admin/slide/NOBODY?token=tok").status_code == 404
    assert c.post("/api/canvas", json={"pid": "F1", "boxes": {"theme": "<script>"}}).status_code == 200
    with study.app.app_context():
        assert study.load_boxes(study.get_db(), "F1")["theme"] == content.THEME_KEYS[0]


def test_misc():
    assert c.get("/study").status_code == 302       # preview pid allowed in tests
    assert c.get("/intro?pid=NOPE").status_code == 302
    # the participant chooses an idea; it is stored, remembered and can change until a box is filled
    start("CH1", "canvas_ai")
    assert c.post("/api/idea", json={"pid": "CH1", "idea": 5}).get_json()["ok"]
    assert "pick idea-chosen" in c.get("/intro?pid=CH1").get_data(as_text=True)
    assert content.IDEAS[4]["name"] in c.get("/canvas?pid=CH1").get_data(as_text=True)
    assert c.post("/api/idea", json={"pid": "CH1", "idea": 9}).status_code == 400
    c.post("/api/canvas", json={"pid": "CH1", "boxes": {"customers": "students nearby"}})
    assert c.post("/api/idea", json={"pid": "CH1", "idea": 2}).get_json()["ok"] is False
    assert c.get("/health").get_json()["status"] == "ok"
    assert c.get("/admin/try/ai").status_code == 403
    if study.ADMIN_TOKEN:
        r = c.get(f"/admin/try/noai?token={study.ADMIN_TOKEN}")
        assert r.status_code == 302 and "PREVIEW-NOAI-" in r.headers["Location"]
        r2 = c.get(f"/admin/try/noai?token={study.ADMIN_TOKEN}")
        assert r2.headers["Location"] != r.headers["Location"]
        assert c.get(f"/admin/try/zzz?token={study.ADMIN_TOKEN}").status_code == 404
    assert c.get("/admin/balance").status_code == 403


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("All canvas tests passed.")
