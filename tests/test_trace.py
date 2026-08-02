"""Traces are the corpus project 2 evaluates, so they must survive being read."""

from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path

import pytest

from arpent.pricing import TokenUsage
from arpent.trace import (
    CallRecord,
    RunRecord,
    Trace,
    purge,
    read_records,
    utc_today,
)


@pytest.fixture
def traces(tmp_path: Path) -> Path:
    return tmp_path / "traces"


def test_a_call_is_costed_and_written_immediately(traces: Path) -> None:
    trace = Trace(query="graphql caching", directory=traces)
    record = trace.record_call(
        step="VALIDATE",
        model="claude-sonnet-5",
        usage=TokenUsage(input_tokens=10_000, output_tokens=1_000),
        duration_ms=1_400,
    )

    assert record.cost_usd == pytest.approx(0.045)
    written = [json.loads(line) for line in trace.path.read_text().splitlines()]
    assert len(written) == 1
    assert written[0]["step"] == "VALIDATE"


def test_the_four_token_fields_survive_the_round_trip(traces: Path) -> None:
    """If any of the four is dropped in serialisation, cost analysis is wrong."""
    trace = Trace(query="q", directory=traces)
    trace.record_call(
        step="PLAN",
        model="claude-haiku-4-5",
        usage=TokenUsage(
            input_tokens=1,
            output_tokens=2,
            cache_creation_input_tokens=3,
            cache_read_input_tokens=4,
        ),
        duration_ms=10,
    )

    (call,) = [r for r in read_records(traces) if isinstance(r, CallRecord)]
    assert call.usage.input_tokens == 1
    assert call.usage.output_tokens == 2
    assert call.usage.cache_creation_input_tokens == 3
    assert call.usage.cache_read_input_tokens == 4


def test_finishing_sums_the_calls(traces: Path) -> None:
    trace = Trace(query="q", directory=traces)
    for _ in range(3):
        trace.record_call(
            step="PLAN",
            model="claude-haiku-4-5",
            usage=TokenUsage(input_tokens=1_000),
            duration_ms=5,
        )

    run = trace.finish(verdict="OPEN", confidence=80, replans=1)
    assert run.calls == 3
    assert run.total_cost_usd == pytest.approx(0.003)
    assert run.verdict == "OPEN"


def test_a_failed_run_still_leaves_a_record(traces: Path) -> None:
    """An execution that leaves no trace is one nobody can learn from."""
    run = Trace(query="q", directory=traces).finish()
    assert run.verdict is None
    assert run.calls == 0

    (record,) = [r for r in read_records(traces) if isinstance(r, RunRecord)]
    assert record.run_id == run.run_id


def test_a_corrupt_line_is_skipped_rather_than_fatal(traces: Path) -> None:
    trace = Trace(query="q", directory=traces)
    trace.record_call(
        step="PLAN",
        model="claude-haiku-4-5",
        usage=TokenUsage(input_tokens=10),
        duration_ms=1,
    )
    with trace.path.open("a", encoding="utf-8") as handle:
        handle.write("{ this is not json\n")

    assert len(read_records(traces)) == 1


def test_purge_removes_only_what_is_past_retention(traces: Path) -> None:
    traces.mkdir(parents=True)
    old = traces / f"{(utc_today() - timedelta(days=120)).isoformat()}.jsonl"
    recent = traces / f"{utc_today().isoformat()}.jsonl"
    old.write_text("")
    recent.write_text("")

    removed = purge(traces, retention_days=90)

    assert removed == [old]
    assert not old.exists()
    assert recent.exists()


def test_retention_is_measured_in_the_same_clock_as_the_filenames(
    traces: Path,
) -> None:
    """Files are named after the UTC date of the run.

    Comparing them against a local ``date.today()`` would purge or skip a
    day's traces around midnight — silently, and only for developers outside
    UTC. The boundary file must survive.
    """
    traces.mkdir(parents=True)
    boundary = traces / f"{(utc_today() - timedelta(days=90)).isoformat()}.jsonl"
    boundary.write_text("")

    assert purge(traces, retention_days=90) == []
    assert boundary.exists()


def test_reading_an_absent_directory_is_not_an_error(tmp_path: Path) -> None:
    assert read_records(tmp_path / "nothing") == []
    assert purge(tmp_path / "nothing", retention_days=90) == []
