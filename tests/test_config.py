"""Settings must stay in step with what .env.example documents.

Documentation drift is the failure this project keeps producing: the CLI moved
to subcommands and two documents kept describing the old flag; the token
estimate outlived the evidence for it. A variable that exists in the code but
not in the example is one nobody knows they can set; one in the example but
not in the code is one that silently does nothing. Both are caught here.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from arpent.config import Limits, Settings, settings

# Fields that are nested models rather than single environment variables.
_NOT_ENV_VARS = {"limits"}


def _documented_variables() -> set[str]:
    text = Path(__file__).resolve().parents[1].joinpath(".env.example").read_text()
    return {m.group(1) for m in re.finditer(r"^([A-Z_]+)=", text, re.MULTILINE)}


def _settings_variables() -> set[str]:
    return {name.upper() for name in Settings.model_fields if name not in _NOT_ENV_VARS}


def test_every_setting_is_documented_in_the_example() -> None:
    missing = _settings_variables() - _documented_variables()
    assert not missing, f"settings absent from .env.example: {sorted(missing)}"


def test_the_example_documents_nothing_the_code_ignores() -> None:
    unknown = _documented_variables() - _settings_variables()
    assert not unknown, f"documented but unread by the code: {sorted(unknown)}"


def test_credentials_are_not_printable(monkeypatch: pytest.MonkeyPatch) -> None:
    """SecretStr is the barrier covering accidental logging.

    Printing a settings object must never reveal a key, however the object is
    rendered.
    """
    secret = "sk-ant-not-a-real-key-0123456789"
    monkeypatch.setenv("ANTHROPIC_API_KEY", secret)
    settings.cache_clear()

    config = Settings()
    assert secret not in repr(config)
    assert secret not in str(config)
    assert config.anthropic_api_key is not None
    assert config.anthropic_api_key.get_secret_value() == secret

    settings.cache_clear()


def test_ceilings_are_not_overridable_from_the_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Deliberate: a ceiling raised by an environment variable on a public
    demo is not a ceiling."""
    monkeypatch.setenv("MAX_PACKAGES", "10000")
    settings.cache_clear()

    assert Settings().limits.max_packages == Limits().max_packages

    settings.cache_clear()


def test_github_enrichment_is_reported_as_unavailable_without_a_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.chdir(Path(__file__).parent)  # away from the developer's .env
    settings.cache_clear()

    assert Settings().github_enrichment_available is False

    settings.cache_clear()
