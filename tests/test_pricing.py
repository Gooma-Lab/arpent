"""Costing must be exact, and must fail loudly when it cannot be."""

from __future__ import annotations

import pytest

from arpent.pricing import (
    TokenUsage,
    UnknownModelError,
    cost_usd,
    min_cacheable_tokens,
    price_for,
)


def test_dated_identifier_resolves_to_the_family_price() -> None:
    assert price_for("claude-haiku-4-5-20251001") == price_for("claude-haiku-4-5")


def test_unknown_model_raises_rather_than_costing_zero() -> None:
    with pytest.raises(UnknownModelError):
        cost_usd("some-other-model", TokenUsage(input_tokens=1_000))


def test_plain_input_and_output_are_billed_at_list_price() -> None:
    # Sonnet 5: $3 per million in, $15 per million out.
    usage = TokenUsage(input_tokens=1_000_000, output_tokens=1_000_000)
    assert cost_usd("claude-sonnet-5", usage) == pytest.approx(18.0)


def test_a_cache_write_costs_more_than_plain_input() -> None:
    """The trap this whole module exists to make visible.

    Writing to the cache is 1.25x input, not a discount. A cache only pays for
    itself from the second read onward.
    """
    written = cost_usd(
        "claude-sonnet-5", TokenUsage(cache_creation_input_tokens=1_000_000)
    )
    plain = cost_usd("claude-sonnet-5", TokenUsage(input_tokens=1_000_000))
    assert written > plain
    assert written == pytest.approx(3.75)


def test_a_cache_read_costs_a_tenth_of_input() -> None:
    read = cost_usd("claude-sonnet-5", TokenUsage(cache_read_input_tokens=1_000_000))
    assert read == pytest.approx(0.30)


def test_total_input_counts_every_token_that_entered_the_model() -> None:
    usage = TokenUsage(
        input_tokens=100,
        output_tokens=999,
        cache_creation_input_tokens=200,
        cache_read_input_tokens=300,
    )
    assert usage.total_input_tokens == 600


def test_both_counters_at_zero_means_the_cache_never_engaged() -> None:
    assert not TokenUsage(input_tokens=5_000).cache_engaged
    assert TokenUsage(cache_read_input_tokens=1).cache_engaged


def test_haiku_needs_a_far_longer_prefix_than_sonnet() -> None:
    """Verified against the documentation, and easy to get wrong.

    A system prompt sized for Sonnet is silently not cached on Haiku.
    """
    assert min_cacheable_tokens("claude-haiku-4-5") == 4_096
    assert min_cacheable_tokens("claude-sonnet-5") == 1_024
    assert min_cacheable_tokens("unknown-model") is None
