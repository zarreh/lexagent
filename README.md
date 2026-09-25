# A6 — LexAgent

> Grounded rental-law reasoning over TX Property Code Ch. 92 + CA Civil Code
> §§1940–1954 and a seeded synthetic precedent corpus.

Portfolio app **A6** (`PORTFOLIO_PLAN_V3.md` §7). Legal / RegTech, Pillar 3 —
Knowledge-Intensive Reasoning. Not deployed publicly yet.

Takes a landlord-tenant legal question, retrieves from both statute and
precedent, reasons with citations, verifies them, and returns a clear answer
with traceable sources — or refuses when the question is outside scope.

## Status

Phase 0 walking skeleton: FastAPI + trivial echo graph + SSE + Next.js UI,
with the full A2 toolchain (ruff, mypy --strict, import-linter, pytest,
MkDocs, Docker compose, GitHub Actions).

## Running it

```bash
uv sync --extra dev
cp .env.example .env   # fill in your own OpenAI API key
make test
make dev               # http://localhost:8000/healthz
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
