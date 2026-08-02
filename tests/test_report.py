"""The cost report is what replaces the unmeasured estimate in DELIVERY.md §10."""

from __future__ import annotations

from pathlib import Path

import pytest

from arpent.pricing import TokenUsage
from arpent.report import build_report, format_report
from arpent.trace import Trace


def _one_run(directory: Path, *, cache_read: int = 0) -> None:
    trace = Trace(query="graphql caching", directory=directory)
    trace.record_call(
        step="PLAN",
        model="claude-haiku-4-5",
        usage=TokenUsage(input_tokens=800, output_tokens=300),
        duration_ms=600,
    )
    trace.record_call(
        step="VALIDATE",
        model="claude-sonnet-5",
        usage=TokenUsage(
            input_tokens=5_000,
            output_tokens=400,
            cache_read_input_tokens=cache_read,
        ),
        duration_ms=1_800,
    )
    trace.record_call(
        step="SYNTHESIZE",
        model="claude-sonnet-5",
        usage=TokenUsage(input_tokens=7_000, output_tokens=1_500),
        duration_ms=3_100,
    )
    trace.finish(verdict="OCCUPIED", confidence=80)


def test_an_empty_directory_says_so_instead_of_printing_zeros(tmp_path: Path) -> None:
    text = format_report(build_report(tmp_path))
    assert "No trace recorded yet" in text
    assert "measurement, not a projection" in text


def test_steps_are_reported_in_loop_order(tmp_path: Path) -> None:
    _one_run(tmp_path)
    report = build_report(tmp_path)
    assert [s.step for s in report.steps] == ["PLAN", "VALIDATE", "SYNTHESIZE"]


def test_per_run_figures_divide_by_the_number_of_runs(tmp_path: Path) -> None:
    _one_run(tmp_path)
    _one_run(tmp_path)

    report = build_report(tmp_path)
    assert report.runs == 2
    assert report.total_calls == 6
    # Per run: 800 + 5 000 + 7 000 in, 300 + 400 + 1 500 out.
    assert report.input_tokens_per_run == 12_800
    assert report.output_tokens_per_run == 2_200


def test_synthesis_dominates_the_bill_in_this_shape(tmp_path: Path) -> None:
    _one_run(tmp_path)
    report = build_report(tmp_path)
    by_step = {s.step: s.cost_usd for s in report.steps}
    assert by_step["SYNTHESIZE"] > by_step["VALIDATE"] > by_step["PLAN"]


def test_a_prefix_under_the_minimum_is_named_as_impossible_to_cache(
    tmp_path: Path,
) -> None:
    """The silent failure the API never reports.

    PLAN sends 800 tokens to Haiku, whose minimum is 4 096. It cannot be
    cached, whatever the code asks for.
    """
    _one_run(tmp_path)
    text = format_report(build_report(tmp_path))
    assert "PLAN on claude-haiku-4-5: cache never engaged" in text
    assert "under this model's 4 096 token minimum" in text


def test_a_long_enough_prefix_gets_the_other_diagnosis(tmp_path: Path) -> None:
    """Two causes, two messages.

    SYNTHESIZE sends 7 000 tokens to Sonnet, well over its 1 024 minimum. The
    cache still did nothing, so the cause is the code, not the model — and
    blaming the minimum here would be its own measurement error.
    """
    _one_run(tmp_path)
    text = format_report(build_report(tmp_path))
    assert "clears the 1 024 token minimum" in text
    assert "cache_control is probably unset" in text


def test_no_warning_once_the_cache_is_actually_used(tmp_path: Path) -> None:
    _one_run(tmp_path, cache_read=6_000)
    text = format_report(build_report(tmp_path))
    assert "VALIDATE on claude-sonnet-5: cache never engaged" not in text


def test_cost_per_run_is_the_number_delivery_section_10_wants(tmp_path: Path) -> None:
    _one_run(tmp_path)
    report = build_report(tmp_path)
    assert report.cost_per_run_usd == pytest.approx(report.total_cost_usd)
