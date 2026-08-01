"""Command-line entry point.

Week 1 scope is deliberately small: prove that the package installs, that the
console script is wired, and that a test can import it. The agent loop arrives
in week 5.
"""

from __future__ import annotations

import argparse
import os
import sys

from arpent import __version__

# Environment variables the project will need, and what happens without them.
# Kept here rather than in config.py so week 1 has no premature abstraction.
_ENV_REQUIREMENTS: list[tuple[str, str]] = [
    ("ANTHROPIC_API_KEY", "required — no model call is possible without it"),
    ("GITHUB_TOKEN", "optional — without it, GitHub enrichment is skipped"),
]


def banner() -> str:
    """Return the one line week 1 is supposed to produce."""
    major, minor, micro = sys.version_info[:3]
    return f"arpent {__version__} — Python {major}.{minor}.{micro}"


def environment_report() -> list[str]:
    """Report which environment variables are set, never their values.

    Printing a key, even truncated, is how keys end up in terminal scrollback
    and in screenshots. Presence is the only thing worth reporting.
    """
    lines = []
    for name, note in _ENV_REQUIREMENTS:
        state = "set" if os.environ.get(name) else "not set"
        lines.append(f"  {name}: {state} ({note})")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="arpent",
        description="Verdicts on technical niches: occupied, open, or desert.",
    )
    parser.add_argument("--version", action="version", version=banner())
    parser.add_argument(
        "--check",
        action="store_true",
        help="report which environment variables are set, without their values",
    )
    args = parser.parse_args(argv)

    print(banner())
    if args.check:
        print("environment:")
        for line in environment_report():
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
