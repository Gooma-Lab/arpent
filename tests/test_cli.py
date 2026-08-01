"""Week 1 smoke tests: the package imports and the entry point runs."""

from __future__ import annotations

import sys

import arpent
from arpent.cli import banner, environment_report, main


def test_interpreter_is_the_pinned_version() -> None:
    """Decision D3: 3.12 locally and in the container.

    Drift between the development interpreter and the deployed one is a listed
    risk, so it fails here rather than at deployment.
    """
    assert sys.version_info[:2] == (3, 12), (
        f"expected Python 3.12, running {sys.version.split()[0]} — "
        "run through `uv run`, which honours .python-version"
    )


def test_package_exposes_a_version() -> None:
    assert arpent.__version__


def test_banner_names_the_tool_and_the_interpreter() -> None:
    line = banner()
    assert line.startswith("arpent ")
    assert f"Python {sys.version_info.major}.{sys.version_info.minor}" in line


def test_main_returns_zero_and_prints_the_banner(capsys) -> None:
    assert main([]) == 0
    assert banner() in capsys.readouterr().out


def test_check_reports_presence_but_never_the_value(monkeypatch, capsys) -> None:
    secret = "sk-ant-not-a-real-key"
    monkeypatch.setenv("ANTHROPIC_API_KEY", secret)

    main(["--check"])

    out = capsys.readouterr().out
    assert "ANTHROPIC_API_KEY: set" in out
    assert secret not in out


def test_check_reports_missing_variables(monkeypatch) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    assert any("GITHUB_TOKEN: not set" in line for line in environment_report())
