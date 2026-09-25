# LexAgent

Grounded rental-law reasoning over Texas Property Code Chapter 92 and
California Civil Code §§1940–1954, plus a seeded synthetic precedent corpus.

## What it does

LexAgent answers landlord–tenant legal questions by retrieving relevant
statute sections and synthetic precedents, reasoning over them with explicit
citations, and verifying those citations before returning an answer. If the
question is outside the supported jurisdictions or the corpus is insufficient,
it refuses rather than hallucinating.

## Status

Phase 0 walking skeleton is complete: FastAPI backend, trivial echo graph,
SSE streaming, Next.js frontend, and the full A2-derived toolchain.
