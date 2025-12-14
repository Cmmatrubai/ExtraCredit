# Extra Credit NL → SQL Demo

## What this is
- React + Vite frontend that takes a natural-language query, calls a FastAPI backend, and displays four things separately: original query, generated SQL, LLM-style narrative, and an interactive sortable results table.
- FastAPI backend with mock data and optional SQLite fallback. Uses lightweight keyword heuristics to generate SQL so it works even without an LLM/API key.

## Project structure
- `backend/` — FastAPI app (`main.py`), demo SQLite seed (`db_seed.sql` + `seed_db.py`), dependencies (`requirements.txt`).
- `frontend/` — React + Vite app with sortable table and cards for query/SQL/LLM output.

## Running locally
1) **Backend**
   - `cd backend`
   - `python -m venv .venv && .venv\\Scripts\\activate` (PowerShell)  
   - `pip install -r requirements.txt`
   - Create `backend/.env` with `GEMINI_API_KEY=...` (see `backend/.env.example`)
   - (Optional) seed SQLite demo data: `python seed_db.py`
   - Run: `uvicorn main:app --reload --port 8000`

2) **Frontend**
   - In a second shell: `cd frontend`
   - `npm install`
   - `npm run dev` (Vite dev server on http://localhost:5173, proxying `/api` to backend)

## Usage
- Enter a natural-language question and submit.
- Backend returns JSON: `{ original_query, generated_sql, columns, rows, llm_output, source }`.
- UI shows:
  - Original query (card)
  - Generated SQL (card)
  - LLM output (card)
  - Interactive table (sortable by header click)
- “New query” resets the form.
- If backend is unreachable, the UI falls back to bundled mock data and notes it.
- If Gemini isn’t used, the UI shows `LLM: Fallback` and a reason (missing key, or Gemini call failed).

## If Gemini falls back
Check the warning under “LLM Output” (it includes the error type/message). Common fixes:
- Reinstall deps after updates: `pip install -r requirements.txt`
- Confirm `backend/.env` contains `GEMINI_API_KEY=...` (no extra spaces in the variable name)
- Restart `uvicorn` after editing `.env`
- Make sure your network/firewall allows outbound HTTPS to Google APIs
- If you see `NotFound: 404 ... model ... not supported`, use a model your key supports (defaults are `gemini-1.5-flash`).

## Recording the required <1 min demo
1. Start backend (`uvicorn ...`) and frontend (`npm run dev`).
2. In the video: show terminal running both servers, then in the browser:
   - Enter a question, submit, show the four panels (query, SQL, LLM text, table).
   - Click a column header to sort.
   - Optionally press “New query” and submit another.
3. Keep it under a minute; you can cut while waiting for responses if needed.

## Notes and extensions
- LLM scripts (for the “include both scripts” requirement): `backend/llm_generate_sql.py` and `backend/llm_answer.py`.
- Backend uses Gemini automatically when `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) is set; otherwise it falls back to local heuristics.
- Attach your real schema and connect to your database by replacing `sample.db` and updating `build_sql`.
- Remember to include **all chat transcripts/citations** with your submission per assignment instructions.
