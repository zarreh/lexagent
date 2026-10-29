"""SQLite-backed store for LexAgent query runs."""

from __future__ import annotations

from pathlib import Path

from zarreh_agentkit.runs import RunEventLog, utc_now

from lexagent.store.models import RunRecord

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
"""


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


class RunStore(RunEventLog):
    """Persists runs, node events, per-node cost, and final answers. Events and
    costs come from `zarreh_agentkit.runs.RunEventLog`; `runs` is this app's own."""

    def __init__(self, db_path: Path) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        super().__init__(db_path)
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def create_run(self, run_id: str, question: str) -> None:
        now = utc_now()
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
            (utc_now(), outcome_kind, answer_json, run_id),
        )
        self._conn.commit()

    def fail_run(self, run_id: str, error: str) -> None:
        self._conn.execute(
            "UPDATE runs SET status = 'failed', updated_at = ?, error = ? WHERE id = ?",
            (utc_now(), error, run_id),
        )
        self._conn.commit()
