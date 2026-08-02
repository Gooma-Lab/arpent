"""Command-line entry point.

Week 2 scope: prove the package runs, report the environment without leaking
it, and turn recorded traces into a cost breakdown. The agent loop arrives in
week 5.
"""

from __future__ import annotations

import argparse
import sys

from arpent import __version__
from arpent.config import settings
from arpent.report import build_report, format_report
from arpent.trace import purge


def banner() -> str:
    """Return the one line week 1 was supposed to produce."""
    major, minor, micro = sys.version_info[:3]
    return f"arpent {__version__} — Python {major}.{minor}.{micro}"


def environment_report() -> list[str]:
    """Report which credentials are present, never their values.

    A key printed once lives in terminal scrollback and in screenshots. This
    is the fourth barrier of ``docs/SECURITY.md`` §6.
    """
    config = settings()
    routing = config.routing
    return [
        f"  ANTHROPIC_API_KEY  {'set' if config.anthropic_api_key else 'NOT SET'}"
        "  (required)",
        f"  GITHUB_TOKEN       {'set' if config.github_token else 'not set'}"
        "  (optional — without it, enrichment is skipped and confidence drops)",
        "",
        f"  planner            {routing.planner}",
        f"  validator          {routing.validator}",
        f"  synthesizer        {routing.synthesizer}",
        "",
        f"  store              {config.arpent_store}",
        f"  traces             {config.arpent_trace_dir}",
    ]


def _cmd_check(_: argparse.Namespace) -> int:
    print(banner())
    print("environment:")
    for line in environment_report():
        print(line)
    return 0 if settings().anthropic_api_key else 1


def _cmd_cost(args: argparse.Namespace) -> int:
    report = build_report(settings().arpent_trace_dir, days=args.days)
    print(format_report(report))
    return 0


def _cmd_purge(_: argparse.Namespace) -> int:
    config = settings()
    removed = purge(config.arpent_trace_dir, config.arpent_trace_retention_days)
    if not removed:
        print(
            f"Nothing older than {config.arpent_trace_retention_days} days "
            "in the trace directory."
        )
    else:
        for path in removed:
            print(f"removed {path}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="arpent",
        description="Verdicts on technical niches: occupied, open, or desert.",
    )
    parser.add_argument("--version", action="version", version=banner())
    subparsers = parser.add_subparsers(dest="command")

    check = subparsers.add_parser(
        "check", help="report which credentials are set, without their values"
    )
    check.set_defaults(func=_cmd_check)

    cost = subparsers.add_parser(
        "cost", help="break recorded traces down by step and model"
    )
    cost.add_argument(
        "--days",
        type=int,
        default=None,
        help="only consider traces from the last N days (default: all)",
    )
    cost.set_defaults(func=_cmd_cost)

    purge_cmd = subparsers.add_parser(
        "purge", help="delete traces past the retention window (DATA.md §3)"
    )
    purge_cmd.set_defaults(func=_cmd_purge)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if getattr(args, "func", None) is None:
        print(banner())
        print("Run `arpent check` to verify the environment.")
        return 0
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
