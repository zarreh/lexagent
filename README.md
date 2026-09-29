# A6 — LexAgent

> Grounded rental-law reasoning over TX Property Code Ch. 92 + CA Civil Code
> §§1940–1954 and a seeded synthetic precedent corpus.

Portfolio app **A6** (`PORTFOLIO_PLAN_V3.md` §7). Legal / RegTech, Pillar 3 —
Knowledge-Intensive Reasoning. Not deployed publicly yet.

Takes a landlord-tenant legal question, retrieves from both statute and
precedent, reasons with citations, verifies them, and returns a clear answer
with traceable sources — or refuses when the question is outside scope.

## Status

`base` complete:

- Phase 0: walking skeleton (FastAPI + echo graph + SSE + Next.js UI)
- Phase 1: seeded TX/CA statute corpus + synthetic precedent corpus
- Phase 2: full LangGraph reasoning loop — parse, dual-corpus retrieval, validate, reason, claim extraction, citation verification, publish/refuse/budget
- Phase 3: `/queries` REST API with SQLite run persistence and SSE streaming
- Phase 4: Next.js query console with live trace timeline and answer panel
- Phase 5: canonical retrieval eval harness + Playwright smoke tests
- Phase 6: GitHub Actions CI for lint/type/test/eval/docs/frontend-e2e
- Phase 7: Docker build + compose verified; production compose with Caddy
- Phase 8: docs finalised

All quality gates green: `make lint typecheck imports test eval`, docs strict,
frontend build + e2e, Docker compose up. Not deployed publicly yet.

## Running it

### Local development

```bash
uv sync --extra dev
cp .env.example .env   # fill in your own OpenAI API key
(cd frontend && npm install)
make test              # backend tests
make eval              # retrieval recall: keyword vs semantic (needs Qdrant for the latter)
make run               # API + UI together -> open http://localhost:3000
make dev               # API only (http://localhost:8000/docs, no UI)
```

Retrieval is semantic: statutes and precedents are embedded (OpenAI
`text-embedding-3-small`) into two Qdrant collections, indexed automatically on
first start. `make run`/`make dev` start Qdrant via Docker; if Qdrant or the
OpenAI key is unavailable the app falls back to the keyword store.

### Production stack (Docker + Caddy)

```bash
cp .env.example .env   # fill in real secrets
make frontend-build    # exports static site to frontend/dist
docker compose -f compose.prod.yaml up -d --build   # http://localhost
```

After rebuilding `frontend/dist`, recreate Caddy so it sees the new files:
`docker compose -f compose.prod.yaml up -d --force-recreate caddy`.

For a real domain, replace `:80` in `Caddyfile` with `lexagent.zarreh.ai` and
remove `auto_https off` so Caddy provisions TLS.

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
