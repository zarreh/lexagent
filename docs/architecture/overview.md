# Architecture overview

LexAgent follows the same layered architecture as the portfolio's other agents:

- `src/lexagent/api/` — FastAPI routes, SSE streaming, middleware.
- `src/lexagent/graph/` — LangGraph state machine, nodes, edges, chains, agents.
- `src/lexagent/tools/` — Tools the agent can call.
- `src/lexagent/retrieval/` — Qdrant-backed vector retrieval for statutes and
  precedents.
- `src/lexagent/schemas/` — Domain state and output models.
- `src/lexagent/prompts/` — Prompt templates.
