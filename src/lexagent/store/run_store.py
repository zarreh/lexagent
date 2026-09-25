"""SQLite-backed store for LexAgent query runs."""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

from lexagent.store.models import RunEvent, RunRecord

_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY,
    question TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    outcome_kind TEXT,
    answer_json TEXT,
    error TEXT
);
CREATE TABLE IF NOT EXISTS run_events (
    run_id TEXT NOT NULL,
    sequence INTEGER NOT NULL,
    node TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (run_id, sequence)
);
"""


def _now() -> str:
    return datetime.now(UTC).isoformat()


def _run_from_row(row: tuple[object, ...]) -> RunRecord:
    return RunRecord(
        id=row[0],  # type: ignore[arg-type]
        question=row[1],  # type: ignore[arg-type]
        status=row[2],  # type: ignore[arg-type]
        created_at=row[3],  # type: ignore[arg-type]
        updated_at=row[4],  # type: ignore[arg-type]
        outcome_kind=row[5],  # type: ignore[arg-type]
        answer_json=row[6],  # type: ignore[arg-type]
        error=row[7],  # type: ignore[arg-type]
    )


class RunStore:
    """Persists runs, node events, and final answers."""

    def __init__(self, db_path: Path) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    def create_run(self, run_id: str, question: str) -> None:
        now = _now()
        self._conn.execute(
            "INSERT INTO runs (id, question, status, created_at, updated_at) "
            "VALUES (?, ?, 'running', ?, ?)",
            (run_id, question, now, now),
        )
        self._conn.commit()

    def get_run(self, run_id: str) -> RunRecord | None:
        row = self._conn.execute(
            "SELECT id, question, status, created_at, updated_at, "
            "outcome_kind, answer_json, error FROM runs WHERE id = ?",
            (run_id,),
        ).fetchone()
        return _run_from_row(row) if row else None

    def complete_run(self, run_id: str, outcome_kind: str, answer_json: str) -> None:
        self._conn.execute(
            "UPDATE runs SET status = 'completed', updated_at = ?, "
            "outcome_kind = ?, answer_json = ? WHERE id = ?",
            (_now(), outcome_kind, answer_json, run_id),
        )
        self._conn.commit()

    def fail_run(self, run_id: str, error: str) -> None:
        self._conn.execute(
            "UPDATE runs SET status = 'failed', updated_at = ?, error = ? WHERE id = ?",
            (_now(), error, run_id),
        )
        self._conn.commit()

    def append_event(self, run_id: str, sequence: int, node: str, payload_json: str) -> None:
        self._conn.execute(
            "INSERT INTO run_events (run_id, sequence, node, payload_json, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (run_id, sequence, node, payload_json, _now()),
        )
        self._conn.commit()

    def get_events(self, run_id: str, after_sequence: int = -1) -> list[RunEvent]:
        rows = self._conn.execute(
            "SELECT sequence, node, payload_json FROM run_events "
            "WHERE run_id = ? AND sequence > ? ORDER BY sequence",
            (run_id, after_sequence),
        ).fetchall()
        return [RunEvent(sequence=row[0], node=row[1], payload_json=row[2]) for row in rows]
