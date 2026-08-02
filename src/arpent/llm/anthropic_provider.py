"""The Anthropic implementation of ``LLMProvider``.

SKELETON — the bodies are yours to write, one TODO at a time. Run
``uv run pytest tests/test_anthropic_provider.py`` after each: the tests are
ordered to match the TODOs, so exactly one more should go green each time.

Everything you need to know about what to produce is in ``provider.py``. This
file only says *how* to get it from one particular SDK.
"""

from __future__ import annotations

from typing import Any

# The SDK's own exception hierarchy. Catching this rather than `Exception`
# means a bug in our own code still crashes loudly instead of being reported
# as a provider failure.
from anthropic import Anthropic, AnthropicError  # noqa: F401

# LLMError and TokenUsage are unused until the TODO bodies exist. The noqa
# keeps the linter quiet without hiding them from you.
from arpent.llm.provider import Completion, LLMError, LLMProvider  # noqa: F401
from arpent.pricing import TokenUsage  # noqa: F401


class AnthropicProvider(LLMProvider):
    """One provider, one SDK, nothing else in the project knows it exists."""

    name = "anthropic"

    def __init__(self, api_key: str | None = None, client: Any | None = None) -> None:
        """Build the provider.

        ``client`` exists so tests can pass a stand-in and never call the real
        API. Production passes ``api_key`` and leaves ``client`` alone. This is
        dependency injection, and it is the reason the test suite costs
        nothing to run.

        TODO 1 — store what you are given.
          * If ``client`` is not None, keep it as ``self._client``.
          * Otherwise build one: ``Anthropic(api_key=api_key)``.
          * If neither is available, raise ``LLMError`` with a message saying
            the key is missing. Failing here is better than failing on the
            first call, three layers deeper.
        """
        raise NotImplementedError("TODO 1")

    def complete(
        self,
        *,
        model: str,
        system: str,
        prompt: str,
        max_tokens: int,
        cache_system: bool = False,
    ) -> Completion:
        """Send one prompt, return one answer.

        TODO 2 — time the call yourself.
          The API does not report how long it took. Use ``time.perf_counter()``
          around the call, and convert the difference to whole milliseconds.

        TODO 3 — build the ``system`` argument.
          When ``cache_system`` is False, a plain string is enough.
          When it is True, the SDK wants a *list of blocks*:
              [{"type": "text", "text": system,
                "cache_control": {"type": "ephemeral"}}]
          Below the model's minimum prefix nothing is cached and no error is
          raised — which is why TODO 5 matters.

        TODO 4 — make the call and read the text out.
          ``client.messages.create(model=..., system=..., max_tokens=...,
          messages=[{"role": "user", "content": prompt}])``
          The answer's ``content`` is a *list of blocks*, not a string. Keep
          the ones whose ``type`` is ``"text"`` and join their ``text``.

        TODO 5 — copy all four token counters into a ``TokenUsage``.
          input_tokens, output_tokens, cache_creation_input_tokens,
          cache_read_input_tokens. The last two may be absent or None on a
          response that used no cache; treat that as 0 rather than letting it
          through.

        TODO 6 — turn SDK failures into ``LLMError``.
          Catch ``AnthropicError`` around the call and re-raise as ``LLMError``
          with the original attached (``raise ... from error``). Nothing
          outside this file should ever have to import an SDK exception.

        Return a ``Completion`` carrying text, model, usage, duration_ms and
        ``stop_reason`` copied straight from the response.
        """
        raise NotImplementedError("TODO 2-6")
