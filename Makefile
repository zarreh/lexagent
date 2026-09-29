.PHONY: run dev test lint typecheck imports eval up down data docs docs-assets frontend-dev frontend-build frontend-types frontend-e2e

run:
	@trap 'kill 0' EXIT INT TERM; \
	uv run uvicorn lexagent.api.main:app --reload --reload-dir src --port 8000 & \
	(cd frontend && npm run dev) & \
	wait

dev:
	uv run uvicorn lexagent.api.main:app --reload --reload-dir src --port 8000

test:
	uv run pytest -v

lint:
	uv run ruff check .
	uv run ruff format --check .

typecheck:
	uv run mypy

imports:
	PYTHONPATH=src uv run lint-imports

eval:
	uv run python -m evals.run

up:
	docker compose up --build

down:
	docker compose down

data:
	uv run python -m data.seed_statutes
	uv run python -m data.seed_precedents
	uv run python -m data.build_vector_store

docs:
	uv run mkdocs serve

docs-assets:
	PYTHONPATH=. uv run python docs/generate_plots.py

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

frontend-types:
	PYTHONPATH=src uv run python -c "from lexagent.api.main import app; import json; json.dump(app.openapi(), open('frontend/openapi.json', 'w'), indent=2)"
	cd frontend && npm run gen:types

frontend-e2e:
	cd frontend && npx playwright test investigation.spec.ts
