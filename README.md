# A6 — LexAgent

> Grounded rental-law reasoning over TX Property Code Ch. 92 + CA Civil Code
> §§1940–1954 and a seeded synthetic precedent corpus.

Portfolio app **A6** (`PORTFOLIO_PLAN_V3.md` §7). Legal / RegTech, Pillar 3 —
Knowledge-Intensive Reasoning. Not deployed publicly yet.

Takes a landlord-tenant legal question, retrieves from both statute and
precedent, reasons with citations, verifies them, and returns a clear answer
with traceable sources — or refuses when the question is outside scope.

## Status

`base` complete through Phase 5:

- Phase 0: walking skeleton (FastAPI + echo graph + SSE + Next.js UI)
- Phase 1: seeded TX/CA statute corpus + synthetic precedent corpus
- Phase 2: full LangGraph reasoning loop — parse, dual-corpus retrieval, validate, reason, claim extraction, citation verification, publish/refuse/budget
- Phase 3: `/queries` REST API with SQLite run persistence and SSE streaming
- Phase 4: Next.js query console with live trace timeline and answer panel
- Phase 5: canonical retrieval eval harness + Playwright smoke tests

All quality gates green: `make lint typecheck imports test eval`, docs strict,
frontend build + e2e. Not deployed publicly yet.

## Running it

```bash
uv sync --extra dev
cp .env.example .env   # fill in your own OpenAI API key
make test              # backend tests
make eval              # canonical retrieval recall eval
make dev               # http://localhost:8000/healthz
cd frontend && npm install && npm run dev   # http://localhost:3000
```

## Layout

| Path | Purpose |
|---|---|
| `docs/` | MkDocs + Material site |
| `src/lexagent/` | The application — `api/`, `graph/`, `tools/`, `retrieval/`, `schemas/`, `prompts/` |
| `data/` | Statute/precedent seeding and vector-store build scripts |
| `evals/` | Evaluation harness |
| `frontend/` | Next.js UI |
| `tests/` | Backend test suite |
| `reference/` | Local-only source material. **Gitignored**, never published |
