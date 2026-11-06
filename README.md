# Side-business canvas study

Two randomised groups see the **same five side-business ideas**, are assigned the **same idea**, and design a
**one-slide business model canvas adapted to side businesses** (nine boxes plus a business name) in the browser.

| Group | What they get |
|---|---|
| `canvas_ai` | The canvas plus an AI co-founder chat panel beside it |
| `canvas_noai` | The same canvas, working alone |

The five ideas (tutoring, social media for local businesses, reselling on Vinted/eBay, dog walking and pet sitting,
personalised gifts) are written for UK university students and people with a main job. Everyone works on idea 3 (`ASSIGNED_IDEA`).

**Interactive, guided flow (both groups):** nine boxes unlock one by one (customers, offer, how they find you, why you,
time, what you need, money in, money out, first 30 days). Each box has a question; the next unlocks after 3 words.
Participants also name the business, write a one-line pitch, pick a slide colour and preview the finished slide.
- `canvas_ai`: a banner highlights the AI co-founder. Opening a box makes it suggest ideas (3 clickable suggestions per box,
  created once); participants reply, use the two helper buttons or add suggestions to their box with one click.
- `canvas_noai`: the same flow with a static guide (things to think about, and an example from another business).

## Flow
`/study?pid=...` (assigns the group) → `/intro` (five ideas, task) → `/canvas` (20 minutes, autosave) → `/done` → survey (`SURVEY_URL`, pid appended).
The timer is a soft limit: when it runs out the slide is handed in as it is and flagged `complete = 0` if fewer than 5 boxes are filled.

## Deploy on Render
1. New private GitHub repo, upload these files (never `.env` or `*.db`).
2. Render: New Web Service, Build `pip install -r requirements.txt`, Start `gunicorn -w 2 -b 0.0.0.0:$PORT app:app`, add a persistent disk and set `DB_PATH` to a file on it.
3. Environment variables: see `.env.example`. Turn **Auto-Deploy off**, upload all files, then one Manual Deploy.
4. Qualtrics link to the study: `https://<your-service>.onrender.com/study?pid=${e://Field/PROLIFIC_PID}`.

## Test links (need `ALLOW_FORCED_CONDITION=1`; set back to 0 for the real study)
- `/study?pid=TESTAI1&cond=canvas_ai`
- `/study?pid=TESTNO1&cond=canvas_noai`

## Data (token protected, `?token=ADMIN_TOKEN`)
- `/admin/export/summary.csv` one row per participant: group, completion, time on canvas, typed AI messages, helper-button clicks, suggestion sets, suggestions used, box opens, prompt words, number of edits, all boxes (JSON)
- `/admin/export/canvases.csv` final text, one column per box
- `/admin/export/canvas_log.csv` every change to every box with a timestamp (editing history)
- `/admin/export/messages.csv` the AI conversation; `events.csv` paste/copy/tab-switch events
- `/admin/slide/<pid>` the participant's slide as a printable page (Print → Save as PDF)
- `/admin/balance`, `/admin/llmtest`

## Before the real study
Freeze `prompts.py`, `content.py` and the model ID; set `ALLOCATION_SEED` once; rotate `ADMIN_TOKEN`; set an Anthropic spend limit;
delete `TEST…` and `PREVIEW-…` participants; run a few real-AI test sessions and read the replies.
