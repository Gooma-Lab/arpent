"""Token accounting: what a call consumed, and what it cost.

Kept apart from ``config`` because it changes for its own reasons — providers
move their prices, and week 11 replays this table against recorded traces.

The rule this module exists to enforce: **read all four token fields**. An
answer reports input, output, cache writes and cache reads separately, and
they are billed at four different rates. Reading only the first two makes a
cache look free when it is not, and makes a cache that never engaged look like
one that did.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

# Cache multipliers applied to the base input price.
# Verified against the Anthropic documentation, August 2026.
CACHE_WRITE_5M_MULTIPLIER = 1.25
CACHE_WRITE_1H_MULTIPLIER = 2.00
CACHE_READ_MULTIPLIER = 0.10

# Minimum prefix length below which a prompt is silently not cached. No error
# is raised — the only evidence is both cache counters coming back zero.
MIN_CACHEABLE_TOKENS: dict[str, int] = {
    "claude-opus-5": 512,
    "claude-sonnet-5": 1_024,
    "claude-haiku-4-5": 4_096,
}


class ModelPrice(BaseModel):
    """List price in dollars per million tokens."""

    input_per_mtok: float
    output_per_mtok: float

    @property
    def cache_write_per_mtok(self) -> float:
        return self.input_per_mtok * CACHE_WRITE_5M_MULTIPLIER

    @property
    def cache_read_per_mtok(self) -> float:
        return self.input_per_mtok * CACHE_READ_MULTIPLIER


# List prices, August 2026.
#
# Sonnet 5 bills at $2/$10 under a promotion running to 2026-08-31. The list
# price is used here on purpose: recorded cost is then an upper bound until
# September, and a budget ceiling should err upward, never downward.
PRICES: dict[str, ModelPrice] = {
    "claude-haiku-4-5": ModelPrice(input_per_mtok=1.0, output_per_mtok=5.0),
    "claude-sonnet-5": ModelPrice(input_per_mtok=3.0, output_per_mtok=15.0),
    "claude-opus-5": ModelPrice(input_per_mtok=5.0, output_per_mtok=25.0),
}


class UnknownModelError(KeyError):
    """Raised when no price is known for a model.

    Deliberately fatal. Silently costing a call at zero is how a budget
    ceiling stops being one.
    """


def price_for(model: str) -> ModelPrice:
    """Resolve a price, accepting dated identifiers.

    ``claude-haiku-4-5-20251001`` resolves to the ``claude-haiku-4-5`` entry,
    so pinning a dated identifier in the environment does not break costing.
    """
    if model in PRICES:
        return PRICES[model]
    for known, price in PRICES.items():
        if model.startswith(known):
            return price
    raise UnknownModelError(
        f"no price known for {model!r} — add it to PRICES rather than "
        "letting the call cost zero"
    )


def min_cacheable_tokens(model: str) -> int | None:
    """Smallest prefix this model will cache, if known."""
    for known, minimum in MIN_CACHEABLE_TOKENS.items():
        if model.startswith(known):
            return minimum
    return None


class TokenUsage(BaseModel):
    """What one call consumed.

    The four fields map one to one onto the ``usage`` block of an API
    response. A provider implementation is expected to copy all four across —
    that is the whole contract between the provider and this module.
    """

    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    cache_creation_input_tokens: int = Field(default=0, ge=0)
    cache_read_input_tokens: int = Field(default=0, ge=0)

    @property
    def total_input_tokens(self) -> int:
        """Every token that entered the model, whatever its billing rate."""
        return (
            self.input_tokens
            + self.cache_creation_input_tokens
            + self.cache_read_input_tokens
        )

    @property
    def cache_engaged(self) -> bool:
        """Whether the cache did anything at all.

        Both counters at zero on a prompt meant to be cached means the prefix
        was under the model's minimum — see ``MIN_CACHEABLE_TOKENS``.
        """
        return bool(self.cache_creation_input_tokens or self.cache_read_input_tokens)


def cost_usd(model: str, usage: TokenUsage) -> float:
    """Cost of one call, in dollars.

    Cache writes cost more than plain input, not less. A cache only pays for
    itself from the second read onward.
    """
    price = price_for(model)
    micro_dollars = (
        usage.input_tokens * price.input_per_mtok
        + usage.output_tokens * price.output_per_mtok
        + usage.cache_creation_input_tokens * price.cache_write_per_mtok
        + usage.cache_read_input_tokens * price.cache_read_per_mtok
    )
    return micro_dollars / 1_000_000
