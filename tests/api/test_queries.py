"""Tests for the /queries lifecycle routes."""

from __future__ import annotations

import time
import uuid
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from lexagent.api.deps import get_lexagent_graph, get_run_store
from lexagent.api.main import app
from lexagent.schemas.legal import LegalAnswer
from lexagent.store.run_store import RunStore


class _FakeGraph:
    async def astream_events(
        self,
        state: dict[str, Any],
        *,
        version: str,
        config: dict[str, Any] | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        _ = version, config
        yield {
            "event": "on_chain_end",
            "metadata": {"langgraph_node": "parse_query"},
            "data": {"output": {"parsed_query": {"question": state.get("question", "")}}},
        }
        yield {
            "event": "on_chain_end",
            "metadata": {"langgraph_node": "retrieve"},
            "data": {"output": {"retrieved_sources": []}},
        }
        answer = LegalAnswer(
            rights="Tenant may recover deposit.",
            obligations="Landlord must return deposit within 30 days.",
            reasoning="Because statute §1 says so.",
            citations=[],
            confidence="high",
            referral_triggered=False,
        )
        yield {
            "event": "on_chain_end",
            "metadata": {"langgraph_node": "publish"},
            "data": {"output": {"answer": answer}},
        }

    async def ainvoke(
        self,
        state: dict[str, Any],
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return state


@pytest.fixture
def tmp_store(tmp_path: Path) -> RunStore:
    return RunStore(tmp_path / "runs.db")


def test_create_and_poll_query(tmp_store: RunStore) -> None:
    app.dependency_overrides[get_lexagent_graph] = lambda: _FakeGraph()
    app.dependency_overrides[get_run_store] = lambda: tmp_store
    try:
        client = TestClient(app)
        response = client.post("/queries", json={"question": "Can my landlord keep my deposit?"})
        assert response.status_code == 202
        run_id = response.json()["id"]

        deadline = time.time() + 5
        while time.time() < deadline:
            status_response = client.get(f"/queries/{run_id}")
            if status_response.json()["status"] == "completed":
                break
            time.sleep(0.05)

        status = status_response.json()
        assert status["question"] == "Can my landlord keep my deposit?"
        assert status["status"] == "completed"
        assert status["outcome_kind"] == "answer"
        assert status["answer"]["rights"] == "Tenant may recover deposit."
        assert status["error"] is None

        events_response = client.get(f"/queries/{run_id}/events")
        assert events_response.status_code == 200
        body = events_response.text
        assert "event: parse_query" in body
        assert "event: publish" in body
        assert "event: done" in body
    finally:
        app.dependency_overrides.clear()


def test_get_unknown_query_returns_404() -> None:
    tmp = RunStore(Path(f"/tmp/runs_{uuid.uuid4().hex}.db"))
    app.dependency_overrides[get_run_store] = lambda: tmp
    try:
        client = TestClient(app)
        response = client.get(f"/queries/{uuid.uuid4()}")
        assert response.status_code == 404

        response = client.get(f"/queries/{uuid.uuid4()}/events")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()
        tmp.close()
