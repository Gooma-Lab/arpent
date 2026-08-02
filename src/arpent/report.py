"""Cost reporting: turn recorded traces into the table week 11 owes.

``docs/DELIVERY.md`` §10 carries an unmeasured estimate — roughly 32k input
and 6k output tokens per run — inherited from a document written before any
code. This module is how that line gets replaced by a measurement.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from pathlib import Path

from arpent.pricing import min_cacheable_tokens
from arpent.trace import CallRecord, RunRecord, read_records


@dataclass
class StepTotals:
    """Everything one step consumed, across every run in the window."""

    step: str
    model: str
    calls: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    cache_write_tokens: int = 0
    cache_read_tokens: int = 0
    cost_usd: float = 0.0

    @property
    def cache_engaged(self) -> bool:
        return bool(self.cache_write_tokens or self.cache_read_tokens)


@dataclass
class CostReport:
    steps: list[StepTotals] = field(default_factory=list)
    runs: int = 0
    total_cost_usd: float = 0.0
    total_calls: int = 0

    @property
    def cost_per_run_usd(self) -> float:
        return self.total_cost_usd / self.runs if self.runs else 0.0

    @property
    def input_tokens_per_run(self) -> int:
        if not self.runs:
            return 0
        total = sum(
            s.input_tokens + s.cache_write_tokens + s.cache_read_tokens
            for s in self.steps
        )
        return round(total / self.runs)

    @property
    def output_tokens_per_run(self) -> int:
        if not self.runs:
            return 0
        return round(sum(s.output_tokens for s in self.steps) / self.runs)


def build_report(directory: Path, days: int | None = None) -> CostReport:
    since = date.today() - timedelta(days=days) if days is not None else None
    records = read_records(directory, since=since)

    buckets: dict[tuple[str, str], StepTotals] = {}
    report = CostReport()

    for record in records:
        if isinstance(record, RunRecord):
            report.runs += 1
            continue
        if not isinstance(record, CallRecord):
            continue

        key = (record.step, record.model)
        totals = buckets.get(key)
        if totals is None:
            totals = StepTotals(step=record.step, model=record.model)
            buckets[key] = totals

        totals.calls += 1
        totals.input_tokens += record.usage.input_tokens
        totals.output_tokens += record.usage.output_tokens
        totals.cache_write_tokens += record.usage.cache_creation_input_tokens
        totals.cache_read_tokens += record.usage.cache_read_input_tokens
        totals.cost_usd += record.cost_usd

        report.total_calls += 1
        report.total_cost_usd += record.cost_usd

    order = {"PLAN": 0, "VALIDATE": 1, "SYNTHESIZE": 2}
    report.steps = sorted(buckets.values(), key=lambda s: order.get(s.step, 99))
    return report


def _thousands(value: int) -> str:
    return f"{value:,}".replace(",", " ")


def format_report(report: CostReport) -> str:
    """Render the report as plain text.

    No colour, no box drawing: this output is meant to be pasted into
    ``DELIVERY.md`` §10.
    """
    if not report.steps:
        return (
            "No trace recorded yet.\n"
            "Run the agent once, then come back — this table is a measurement, "
            "not a projection."
        )

    header = f"{'step':<12} {'model':<20} {'calls':>6} {'in':>9} {'out':>8} "
    header += f"{'cache r':>9} {'cost':>10}  share"
    lines = [header, "-" * len(header)]

    for totals in report.steps:
        share = (
            totals.cost_usd / report.total_cost_usd * 100
            if report.total_cost_usd
            else 0.0
        )
        lines.append(
            f"{totals.step:<12} {totals.model:<20} {totals.calls:>6} "
            f"{_thousands(totals.input_tokens):>9} "
            f"{_thousands(totals.output_tokens):>8} "
            f"{_thousands(totals.cache_read_tokens):>9} "
            f"${totals.cost_usd:>9.4f}  {share:>5.1f}%"
        )

    lines.append("-" * len(header))
    lines.append(
        f"{'TOTAL':<12} {'':<20} {report.total_calls:>6} "
        f"{'':>9} {'':>8} {'':>9} ${report.total_cost_usd:>9.4f}"
    )
    lines.append("")
    lines.append(f"runs                  {report.runs}")
    lines.append(f"cost per run          ${report.cost_per_run_usd:.4f}")
    lines.append(f"input tokens per run  {_thousands(report.input_tokens_per_run)}")
    lines.append(f"output tokens per run {_thousands(report.output_tokens_per_run)}")

    warnings = _cache_warnings(report)
    if warnings:
        lines.append("")
        lines.extend(warnings)

    return "\n".join(lines)


def _cache_warnings(report: CostReport) -> list[str]:
    """Flag steps where the cache never engaged, and say which cause applies.

    Both counters at zero has two quite different explanations, and reporting
    one message for both would be its own measurement error:

    * the prefix is under the model's minimum, so caching is impossible;
    * the prefix is long enough, so either ``cache_control`` was never set or
      the prefix changes between calls.

    The API reports neither. This is the only place either surfaces.
    """
    warnings = []
    for totals in report.steps:
        if totals.cache_engaged or not totals.calls:
            continue
        minimum = min_cacheable_tokens(totals.model)
        if minimum is None:
            continue

        average_input = totals.input_tokens // totals.calls
        prefix = f"! {totals.step} on {totals.model}: cache never engaged"
        if average_input < minimum:
            warnings.append(
                f"{prefix} — average input {_thousands(average_input)} is under "
                f"this model's {_thousands(minimum)} token minimum, so it cannot "
                "be cached at all."
            )
        else:
            warnings.append(
                f"{prefix} — average input {_thousands(average_input)} clears the "
                f"{_thousands(minimum)} token minimum, so cache_control is "
                "probably unset, or the prefix changes between calls."
            )
    return warnings
