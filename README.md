# Enterprise Multi-Agent Operations Copilot

A local-first, production-structured multi-agent system for enterprise operations workflows —
not a chatbot. A LangGraph **Planner** decomposes each request, routes it to the specialist
agents that are actually needed, and composes their structured outputs into one cited answer.

Everything runs locally: **FastAPI + LangGraph + LangChain** on the backend, a local **Ollama**
model for inference, **ChromaDB** for vector search, **SQLite** for conversation/artifact memory,
and a **Next.js + Tailwind + ShadCN** chat UI on the frontend.

## Agents

| Agent | What it does |
|---|---|
| **Planner** | The LangGraph supervisor itself. Reads the request + conversation context, decides which agents are needed, builds an ordered step plan, and retries/degrades gracefully on failure. |
| **RAG** | Chunks and embeds uploaded PDFs into a per-conversation ChromaDB collection; answers questions with `(filename, page)` citations. |
| **Data Analysis** | Runs EDA over uploaded CSV/Excel (missing values, summary stats, correlations), renders a correlation heatmap, and writes business insights. |
| **Python Execution** | Generates Python (pandas/matplotlib/plotly) from the request, runs it in an isolated subprocess with a timeout + memory watchdog, and self-corrects on failure using the error message. |
| **Forecasting** | Projects a numeric metric forward using a linear trend over detected historical periods, with a confidence band chart and narrative — distinct from Data Analysis (which describes the past) and Python Exec (arbitrary code). |
| **Report** | Assembles everything produced so far into a Markdown report, then exports PDF and PowerPoint versions. |
| **Mail** | Emails previously generated artifacts (reports, charts) to a recipient extracted from the request. |
| **Memory** | Persists conversation turns, uploaded files, and artifacts in SQLite; hydrates context for follow-up questions every turn. |

## Architecture

```
User uploads PDFs/CSV/XLSX + asks a question
        │
        ▼
   load_memory  ──► hydrates context from SQLite (history, files, prior artifacts)
        │
        ▼
     planner  ──► builds an ordered step plan (or none, for plain chat)
        │
        ▼
  ┌─────┴──────┬────────────┬─────────────┬──────────┬───────┐
  rag   data_analysis   python_exec   forecast   report   mail   (routed per-step)
  └─────┬──────┴────────────┴─────────────┴──────────┴───────┘
        │  (loops back to planner between steps; retries failed
        │   steps up to MAX_AGENT_RETRIES before degrading gracefully)
        ▼
   synthesize  ──► streams the final cited answer
        │
        ▼
   save_memory  ──► persists messages + artifacts + per-agent trace to SQLite
```

Each chat turn runs on its own LangGraph checkpointer thread — cross-turn memory is handled
explicitly via SQLite (`load_memory`/`save_memory`), not via LangGraph's checkpoint replay, so one
turn's plan/artifacts never leak into the next.

## Project layout

```
backend/
  app/
    agents/      # one package per agent (planner, rag, data_analysis, python_exec,
                  #   forecast, report, mail, memory) - schemas + service logic + graph node
    graph/        # GraphState, the supervisor graph builder, routing
    api/          # FastAPI routes (conversations, files, chat SSE, artifacts) + DI
    db/           # SQLAlchemy models/CRUD (conversations, messages, files, artifacts, agent_runs)
    vectorstore/  # ChromaDB client, per-conversation collections
    llm/          # provider-agnostic chat/embedding factory (Ollama now, OpenAI/Gemini pluggable)
    core/         # settings (.env) + logging
  scripts/        # sample-data seeding + end-to-end smoke tests
frontend/
  app/conversations/[id]/   # chat workspace (upload, chat, plan/agent trace, artifacts)
  components/               # chat, upload, agent-trace, artifact-viewer components
  lib/                      # typed API client, hand-rolled SSE parser, chat hook
```

## Prerequisites

- [Ollama](https://ollama.com) running locally, with:
  ```
  ollama pull qwen2.5:7b-instruct
  ollama pull nomic-embed-text
  ```
- [uv](https://docs.astral.sh/uv/) for the Python environment (Python 3.11)
- Node.js 18+ / npm

## Running it

**Backend:**
```
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```
`GET http://localhost:8000/api/health` should report `"ollama": "reachable"`.

**Frontend:**
```
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` — it creates a conversation and redirects you straight in.

## Configuration

Backend settings live in `backend/.env` (copy from `.env.example`). Key groups:

- **LLM**: `LLM_PROVIDER` (`ollama` default; `openai`/`gemini` also supported), `OLLAMA_MODEL`,
  `OLLAMA_EMBED_MODEL`, `OLLAMA_BASE_URL`.
- **Storage paths**: `SQLITE_PATH`, `CHROMA_DIR`, `UPLOAD_DIR`, `ARTIFACT_DIR` (all under `data/`).
- **Sandbox**: `SANDBOX_TIMEOUT_SECONDS`, `SANDBOX_MEMORY_LIMIT_MB`, `MAX_AGENT_RETRIES`.
- **Mail Agent**: `SMTP_HOST`, `SMTP_PORT`, `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_ADDRESS`,
  `SMTP_USE_TLS`. Leave `SMTP_HOST` empty to disable emailing — the agent will say so instead of
  failing silently. For local testing without a real mail account, run
  `uv run python scripts/debug_smtp_server.py` (needs the `aiosmtpd` dev dependency, already in
  `pyproject.toml`) and point `SMTP_HOST=localhost`, `SMTP_PORT=1025`, `SMTP_USE_TLS=false` at it;
  received mail is saved to `backend/scripts/received_mail/*.eml`.
- **Forecasting Agent**: `FORECAST_PERIODS_AHEAD` (how many future periods to project).

## Verifying it end-to-end

```
cd backend
uv run python scripts/seed_sample_files.py     # writes scripts/sample_data/{sample.csv,sample.pdf}
uv run python scripts/smoke_test.py            # upload + RAG + data analysis, over real HTTP/SSE
uv run python scripts/smoke_test_extra.py      # python execution + report generation
uv run python scripts/smoke_test_mail_forecast.py  # forecast -> report -> mail, multi-turn
```

## Known limitations

- **The Python sandbox is process isolation, not a security boundary.** It runs generated code in
  a fresh subprocess with a timeout and an RSS memory watchdog so a bad script can't hang or crash
  the server — but it does not stop deliberately malicious code from touching the filesystem. This
  is an accepted tradeoff for a single-user local tool; see `app/agents/python_exec/sandbox.py`.
- **Forecasting uses a simple linear trend**, not a full time-series model — appropriate for small
  ad hoc business exports, called out explicitly in the agent's own narrative output.
- **ChromaDB collections are per-conversation**, so document retrieval is scoped to files uploaded
  in that conversation only.
