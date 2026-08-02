"""Guide for writing AnthropicProvider — one test per TODO, in order.

Nothing here touches the network. ``FakeClient`` mimics the shape the SDK
returns, so the whole file runs in milliseconds and costs nothing.

Run just this file while you work:

    uv run pytest tests/test_anthropic_provider.py -x

``-x`` stops at the first failure, which is the one you are working on.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from arpent.llm.anthropic_provider import AnthropicProvider
from arpent.llm.provider import LLMError
from tests.test_provider import ProviderContract

# Deselected in CI while the bodies are unwritten. **Delete this line when the
# last TODO is done** — that is what puts the implementation under the merge
# gates, and it is the only signal that the work is finished.
pytestmark = pytest.mark.wip


class FakeMessages:
    """Stands in for ``client.messages``.

    It records what it was called with, which is how the tests check that the
    request was built correctly without ever sending it.
    """

    def __init__(self, response: Any, error: Exception | None = None) -> None:
        self._response = response
        self._error = error
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: Any) -> Any:
        self.calls.append(kwargs)
        if self._error is not None:
            raise self._error
        return self._response


class FakeClient:
    def __init__(self, response: Any, error: Exception | None = None) -> None:
        self.messages = FakeMessages(response, error)


def make_response(
    text: str = "hello",
    stop_reason: str = "end_turn",
    model: str = "claude-sonnet-5",
    cache_creation: int | None = 0,
    cache_read: int | None = 0,
) -> SimpleNamespace:
    """Mimic the shape of a real Anthropic response.

    Note two things the real SDK does and that trip people up:
      * ``content`` is a *list of blocks*, not a string.
      * the cache counters can be absent or None when no cache was involved.
    """
    return SimpleNamespace(
        content=[SimpleNamespace(type="text", text=text)],
        model=model,
        stop_reason=stop_reason,
        usage=SimpleNamespace(
            input_tokens=120,
            output_tokens=45,
            cache_creation_input_tokens=cache_creation,
            cache_read_input_tokens=cache_read,
        ),
    )


# --------------------------------------------------------------------------
# TODO 1 — the constructor
# --------------------------------------------------------------------------


def test_an_injected_client_is_used_as_is() -> None:
    client = FakeClient(make_response())
    provider = AnthropicProvider(client=client)
    assert provider._client is client


def test_a_missing_key_fails_at_construction_not_at_first_call() -> None:
    """Fail where the mistake was made, not three layers deeper."""
    with pytest.raises(LLMError, match="(?i)key"):
        AnthropicProvider(api_key=None)


# --------------------------------------------------------------------------
# TODO 2 — timing
# --------------------------------------------------------------------------


def test_the_call_is_timed() -> None:
    provider = AnthropicProvider(client=FakeClient(make_response()))
    completion = provider.complete(
        model="claude-sonnet-5", system="s", prompt="p", max_tokens=64
    )
    assert isinstance(completion.duration_ms, int)
    assert completion.duration_ms >= 0


# --------------------------------------------------------------------------
# TODO 3 — the system argument
# --------------------------------------------------------------------------


def test_without_caching_the_system_prompt_is_a_plain_string() -> None:
    client = FakeClient(make_response())
    AnthropicProvider(client=client).complete(
        model="claude-sonnet-5", system="be terse", prompt="p", max_tokens=64
    )
    assert client.messages.calls[0]["system"] == "be terse"


def test_with_caching_the_system_prompt_becomes_a_marked_block() -> None:
    client = FakeClient(make_response())
    AnthropicProvider(client=client).complete(
        model="claude-sonnet-5",
        system="be terse",
        prompt="p",
        max_tokens=64,
        cache_system=True,
    )
    system = client.messages.calls[0]["system"]
    assert isinstance(system, list)
    assert system[0]["text"] == "be terse"
    assert system[0]["cache_control"] == {"type": "ephemeral"}


# --------------------------------------------------------------------------
# TODO 4 — the request and the text
# --------------------------------------------------------------------------


def test_the_prompt_is_sent_as_a_user_message() -> None:
    client = FakeClient(make_response())
    AnthropicProvider(client=client).complete(
        model="claude-haiku-4-5", system="s", prompt="how many?", max_tokens=64
    )
    call = client.messages.calls[0]
    assert call["model"] == "claude-haiku-4-5"
    assert call["max_tokens"] == 64
    assert call["messages"] == [{"role": "user", "content": "how many?"}]


def test_text_blocks_are_joined_into_one_string() -> None:
    """``content`` is a list. Returning it raw, or taking only the first
    block, are the two usual mistakes."""
    response = make_response()
    response.content = [
        SimpleNamespace(type="text", text="first "),
        SimpleNamespace(type="text", text="second"),
    ]
    provider = AnthropicProvider(client=FakeClient(response))

    completion = provider.complete(
        model="claude-sonnet-5", system="s", prompt="p", max_tokens=64
    )
    assert completion.text == "first second"


def test_non_text_blocks_are_ignored() -> None:
    response = make_response()
    response.content = [
        SimpleNamespace(type="thinking", thinking="ignore me"),
        SimpleNamespace(type="text", text="keep me"),
    ]
    provider = AnthropicProvider(client=FakeClient(response))

    completion = provider.complete(
        model="claude-sonnet-5", system="s", prompt="p", max_tokens=64
    )
    assert completion.text == "keep me"


def test_the_stop_reason_is_carried_across() -> None:
    """Without it, `truncated` is always False and a cut-off answer looks
    like a refusal."""
    provider = AnthropicProvider(
        client=FakeClient(make_response(stop_reason="max_tokens"))
    )
    completion = provider.complete(
        model="claude-sonnet-5", system="s", prompt="p", max_tokens=8
    )
    assert completion.stop_reason == "max_tokens"
    assert completion.truncated


# --------------------------------------------------------------------------
# TODO 5 — the four counters
# --------------------------------------------------------------------------


def test_all_four_counters_are_copied() -> None:
    provider = AnthropicProvider(
        client=FakeClient(make_response(cache_creation=900, cache_read=3_400))
    )
    usage = provider.complete(
        model="claude-sonnet-5", system="s", prompt="p", max_tokens=64
    ).usage

    assert usage.input_tokens == 120
    assert usage.output_tokens == 45
    assert usage.cache_creation_input_tokens == 900
    assert usage.cache_read_input_tokens == 3_400


def test_absent_cache_counters_become_zero_not_none() -> None:
    """A response that used no cache may report None. TokenUsage refuses it,
    and a crash here would be a crash on every uncached call."""
    provider = AnthropicProvider(
        client=FakeClient(make_response(cache_creation=None, cache_read=None))
    )
    usage = provider.complete(
        model="claude-sonnet-5", system="s", prompt="p", max_tokens=64
    ).usage

    assert usage.cache_creation_input_tokens == 0
    assert usage.cache_read_input_tokens == 0
    assert not usage.cache_engaged


# --------------------------------------------------------------------------
# TODO 6 — failures
# --------------------------------------------------------------------------


def test_an_sdk_failure_surfaces_as_an_llm_error() -> None:
    """Nothing outside this file should have to import an SDK exception."""
    from anthropic import APIConnectionError

    client = FakeClient(
        make_response(),
        error=APIConnectionError(request=None),  # type: ignore[arg-type]
    )
    provider = AnthropicProvider(client=client)

    with pytest.raises(LLMError):
        provider.complete(
            model="claude-sonnet-5", system="s", prompt="p", max_tokens=64
        )


# --------------------------------------------------------------------------
# The shared contract — the real finish line
# --------------------------------------------------------------------------


class TestAnthropicProviderContract(ProviderContract):
    """Once this passes unchanged, the implementation is interchangeable with
    any other provider — which is the whole point of the seam."""

    @pytest.fixture
    def provider(self) -> AnthropicProvider:
        return AnthropicProvider(client=FakeClient(make_response()))
