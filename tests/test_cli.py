"""The entry point must never print a secret, whatever it is asked."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

import arpent
from arpent.cli import banner, environment_report, main
from arpent.config import settings


@pytest.fixture(autouse=True)
def isolated_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """Keep tests off the developer's real .env and trace directory."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    settings.cache_clear()
    yield
    settings.cache_clear()


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


def test_bare_invocation_points_at_check(capsys: pytest.CaptureFixture) -> None:
    assert main([]) == 0
    assert "arpent check" in capsys.readouterr().out


def test_check_reports_presence_but_never_the_value(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    secret = "sk-ant-not-a-real-key-0123456789"
    monkeypatch.setenv("ANTHROPIC_API_KEY", secret)
    settings.cache_clear()

    assert main(["check"]) == 0

    out = capsys.readouterr().out
    assert "ANTHROPIC_API_KEY  set" in out
    assert secret not in out
    assert "sk-ant" not in out


def test_check_fails_without_the_required_key() -> None:
    """A missing Anthropic key is fatal; a missing GitHub token is not."""
    assert main(["check"]) == 1


def test_check_reports_a_missing_github_token_without_failing() -> None:
    report = "\n".join(environment_report())
    assert "GITHUB_TOKEN       not set" in report


def test_cost_on_an_empty_directory_reports_nothing_measured(
    capsys: pytest.CaptureFixture,
) -> None:
    assert main(["cost"]) == 0
    assert "No trace recorded yet" in capsys.readouterr().out


def test_purge_says_when_there_is_nothing_to_remove(
    capsys: pytest.CaptureFixture,
) -> None:
    assert main(["purge"]) == 0
    assert "Nothing older than 90 days" in capsys.readouterr().out
