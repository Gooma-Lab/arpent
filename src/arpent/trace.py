"""Execution traces, written as JSONL.

Every run records what it planned, what it spent, and what it concluded. Two
reasons, and the second is the important one:

1. It is how the token budget stops being an estimate — see ``docs/DELIVERY.md``
   §10, which currently holds an unmeasured figure this module is meant to
   replace.
2. It is the corpus project 2 evaluates. Traces written from week 2 mean the
   evaluation suite starts with data instead of spending two weeks collecting
   it.

No database. Lines of JSON on disk, pushed to a Hugging Face dataset — see
``docs/ARCHITECTURE.md`` §5 for why Supabase was dropped.
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from arpent.pricing import TokenUsage, cost_usd

Step = Literal["PLAN", "VALIDATE", "SYNTHESIZE"]
Verdict = Literal["OCCUPIED", "OPEN", "DESERT"]


class CallRecord(BaseModel):
    """One model call."""

    kind: Literal["call"] = "call"
    run_id: str
    at: datetime
    step: Step
    model: str
    usage: TokenUsage
    cost_usd: float
    duration_ms: int


class RunRecord(BaseModel):
    """One complete run, written last."""

    kind: Literal["run"] = "run"
    run_id: str
    at: datetime
    query: str
    verdict: Verdict | None = None
    confidence: int | None = None
    replans: int = 0
    calls: int = 0
    total_cost_usd: float = 0.0
    duration_ms: int = 0
    # Free text, one entry per thing that could not be measured.
    blind_spots: list[str] = Field(default_factory=list)


def _now() -> datetime:
    return datetime.now(UTC)


class Trace:
    """Collects the records of a single run and appends them to a JSONL file.

    One file per day, so purging by retention is a matter of deleting files
    rather than rewriting them.
    """

    def __init__(self, query: str, directory: Path, run_id: str | None = None) -> None:
        self.run_id = run_id or uuid.uuid4().hex[:12]
        self.query = query
        self.directory = directory
        self.started_at = _now()
        self.calls: list[CallRecord] = []

    @property
    def path(self) -> Path:
        return self.directory / f"{self.started_at.date().isoformat()}.jsonl"

    @property
    def total_cost_usd(self) -> float:
        return sum(call.cost_usd for call in self.calls)

    def record_call(
        self,
        step: Step,
        model: str,
        usage: TokenUsage,
        duration_ms: int,
    ) -> CallRecord:
        """Record one model call and return what it cost.

        Raises if the model has no known price rather than costing it at zero.
        """
        record = CallRecord(
            run_id=self.run_id,
            at=_now(),
            step=step,
            model=model,
            usage=usage,
            cost_usd=cost_usd(model, usage),
            duration_ms=duration_ms,
        )
        self.calls.append(record)
        self._append(record)
        return record

    def finish(
        self,
        verdict: Verdict | None = None,
        confidence: int | None = None,
        replans: int = 0,
        blind_spots: list[str] | None = None,
    ) -> RunRecord:
        """Close the run and write its summary line.

        A run that failed still gets a record, with ``verdict`` left None. An
        execution that leaves no trace is an execution nobody can learn from,
        and a failure is exactly what one wants to learn from.
        """
        finished = _now()
        record = RunRecord(
            run_id=self.run_id,
            at=finished,
            query=self.query,
            verdict=verdict,
            confidence=confidence,
            replans=replans,
            calls=len(self.calls),
            total_cost_usd=self.total_cost_usd,
            duration_ms=int((finished - self.started_at).total_seconds() * 1000),
            blind_spots=blind_spots or [],
        )
        self._append(record)
        return record

    def _append(self, record: BaseModel) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        line = record.model_dump_json()
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")


def read_records(
    directory: Path, since: date | None = None
) -> list[CallRecord | RunRecord]:
    """Read every record on disk, newest files last.

    A malformed line is skipped rather than fatal: a corrupted trace should
    never stop a cost report.
    """
    if not directory.exists():
        return []

    records: list[CallRecord | RunRecord] = []
    for path in sorted(directory.glob("*.jsonl")):
        if since is not None:
            try:
                if date.fromisoformat(path.stem) < since:
                    continue
            except ValueError:
                pass
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
                if payload.get("kind") == "call":
                    records.append(CallRecord.model_validate(payload))
                elif payload.get("kind") == "run":
                    records.append(RunRecord.model_validate(payload))
            except (json.JSONDecodeError, ValueError):
                continue
    return records


def purge(directory: Path, retention_days: int) -> list[Path]:
    """Delete trace files older than the retention window (DATA.md §3).

    Returns what was removed, so the caller can report it rather than delete
    in silence.
    """
    if not directory.exists():
        return []

    cutoff = date.today() - timedelta(days=retention_days)
    removed: list[Path] = []
    for path in sorted(directory.glob("*.jsonl")):
        try:
            file_date = date.fromisoformat(path.stem)
        except ValueError:
            continue
        if file_date < cutoff:
            path.unlink()
            removed.append(path)
    return removed
