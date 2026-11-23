# Run on its own: python -m pytest test_machine.py   (machine mode is chosen at start-up with UI_MODE=machine)
import csv, io, os, tempfile
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
        assert "Develop your small entrepreneurial project" in intro
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
    assert "3 to 5 words" in sim and "1 of 9 parts have text" in sim and "Which area: big city" in sim
    assert "Mobile bike repairs for commuters" in sim
    chat = prompts.system_prompt(own, {}, "customers", "chat", machine=True)
    assert "tapped one of your chips" in chat
    # greeting carries the participant's idea; tapped chips are quick replies, capped separately from typed messages
    assert c.get("/study?pid=MQ&cond=canvas_ai").status_code == 302
    c.post("/api/idea", json={"pid": "MQ", "text": "Mobile bike repairs for commuters"})
    assert "Mobile bike repairs for commuters" in c.get("/canvas?pid=MQ").get_data(as_text=True)
    r = c.post("/api/chat", json={"pid": "MQ", "message": "Group walks first", "box": "problem", "boxes": {}, "quick": "choice"})
    assert r.status_code == 200 and r.get_json()["reply"]
    with study.app.app_context():
        kinds = [x["kind"] for x in study.get_db().execute("SELECT kind FROM messages WHERE pid = 'MQ' AND role = 'user'")]
        assert kinds == ["quick"]


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("All machine tests passed.")
