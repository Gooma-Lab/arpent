"""Ceilings, model routing, and credentials.

Every ceiling here is fixed before execution, never computed during it. A limit
worked out at runtime is a limit that can be argued with.

Sources: the per-run ceilings are decision D14; the routing is D8; both are
documented in ``docs/DELIVERY.md`` and ``docs/SECURITY.md``.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Limits(BaseModel):
    """Per-run ceilings (D14).

    ``max_seconds`` is 100 against a stated promise of 120: the gap is the
    margin, and it is deliberate. A promise met exactly is a promise about to
    be broken.
    """

    max_packages: int = 40
    # Revised down from 250 after the 2026-08-02 probe: npm search returns
    # downloads, dependents, the publish date and the repository URL in a
    # single call, so the npm side costs 1-2 calls rather than one per package.
    # What remains is GitHub enrichment, one call per package.
    max_http_calls: int = 60
    max_concurrency: int = 8
    max_replans: int = 2
    max_input_tokens: int = 60_000
    max_output_tokens: int = 8_000
    max_seconds: float = 100.0
    daily_cost_ceiling_usd: float = 1.00
    collect_cache_ttl_seconds: int = 1_800


class ModelRouting(BaseModel):
    """Which model runs which step (D8).

    The validator does not run on the cheap model. It is the step that carries
    the value of the project, and the gap is a few cents a run.
    """

    planner: str
    validator: str
    synthesizer: str


class Settings(BaseSettings):
    """Everything read from the environment.

    Credentials are ``SecretStr``: printing or logging a settings object shows
    ``**********`` rather than the key. That is not decoration — it is the
    fourth barrier of ``docs/SECURITY.md`` §6, the one covering terminal
    scrollback and screenshots.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    anthropic_api_key: SecretStr | None = None
    github_token: SecretStr | None = None

    arpent_store: Literal["jsonl"] = "jsonl"
    arpent_trace_dir: Path = Path("data/traces")
    arpent_trace_retention_days: int = 90  # DATA.md §3

    arpent_model_planner: str = "claude-haiku-4-5"
    arpent_model_validator: str = "claude-sonnet-5"
    arpent_model_synthesizer: str = "claude-sonnet-5"

    limits: Limits = Field(default_factory=Limits)

    @property
    def routing(self) -> ModelRouting:
        return ModelRouting(
            planner=self.arpent_model_planner,
            validator=self.arpent_model_validator,
            synthesizer=self.arpent_model_synthesizer,
        )

    @property
    def github_enrichment_available(self) -> bool:
        """Whether GitHub enrichment can run at all.

        False is not an error. The verdict is still produced, confidence drops
        by 25, and the missing source is named — ``docs/DESIGN.md`` §6.
        """
        return self.github_token is not None


@lru_cache(maxsize=1)
def settings() -> Settings:
    """The process-wide settings, read once."""
    return Settings()
