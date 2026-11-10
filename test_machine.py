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
        intro = c.get(f"/intro?pid={pid}").get_data(as_text=True)
        assert "Build your own money machine" in intro
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


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("All machine tests passed.")
