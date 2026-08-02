"""The seam between the agent and whoever answers it.

Three things this interface enforces by shape rather than by discipline:

**No tools.** There is no parameter for them. The validator and the
synthesiser must be unable to call, write or spend — ``docs/SECURITY.md`` §2 —
and the cheapest way to guarantee that is an interface through which a tool
cannot be passed at all.

**No vendor types.** Nothing here mentions a provider. Project 2 replays the
same cases against a second provider, and that costs nothing extra only
because no caller ever sees an SDK object.

**No permissive parsing.** ``complete_as`` either returns a valid model or
raises. A malformed answer is an error, never a best guess — an injected
instruction that produced junk must not be quietly repaired into something
plausible.
"""

from __future__ import annotations

import json
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TypeVar

from pydantic import BaseModel, ValidationError

from arpent.pricing import TokenUsage

T = TypeVar("T", bound=BaseModel)


class LLMError(RuntimeError):
    """Anything that stopped a call from producing a usable answer."""


class MalformedOutputError(LLMError):
    """The answer did not fit the requested shape.

    Raised rather than repaired. ``docs/SECURITY.md`` §2: any output that does
    not match the closed format triggers an error, not a permissive reading.
    """


@dataclass(frozen=True)
class Completion:
    """One answer, and what it cost to obtain.

    ``usage`` carries all four token counters. A provider that fills only
    ``input_tokens`` and ``output_tokens`` makes an absent cache look like a
    working one — see ``arpent.pricing``.
    """

    text: str
    model: str
    usage: TokenUsage
    duration_ms: int
    stop_reason: str | None = None

    @property
    def truncated(self) -> bool:
        """Whether the answer was cut short by the output ceiling.

        A truncated answer still produces a verdict, carrying a truncation
        notice — ``docs/DESIGN.md`` §6. It is never silently treated as
        complete.
        """
        return self.stop_reason in {"max_tokens", "length"}


def as_data(content: str, label: str = "collected_data") -> str:
    """Wrap third-party text so it reads as data, never as instruction.

    Package descriptions and repository readmes are written by strangers, and
    a hostile one is cheap to publish. Everything collected passes through
    here before reaching a prompt.

    The closing tag is stripped from the content itself: without that, text
    containing ``</collected_data>`` could close the block early and have
    whatever follows read as instruction.
    """
    closing = f"</{label}>"
    safe = content.replace(closing, closing.replace("<", "‹"))
    return f"<{label}>\n{safe}\n{closing}"


_JSON_BLOCK = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL)


def extract_json(text: str) -> str:
    """Pull the JSON payload out of an answer.

    Models wrap JSON in fences often enough that refusing to unwrap them would
    be pedantry rather than rigour. Anything beyond that — prose around an
    object, a truncated brace — is left to fail validation.
    """
    match = _JSON_BLOCK.search(text)
    if match:
        return match.group(1).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        return text[start : end + 1]
    return text.strip()


class LLMProvider(ABC):
    """One provider. Implementations live beside this file.

    Subclasses implement ``complete`` and nothing else; ``complete_as`` is
    given for free, so structured parsing behaves identically whoever answers.
    That uniformity is what makes a two-provider comparison meaningful.
    """

    name: str

    @abstractmethod
    def complete(
        self,
        *,
        model: str,
        system: str,
        prompt: str,
        max_tokens: int,
        cache_system: bool = False,
    ) -> Completion:
        """Send one prompt and return one answer.

        ``cache_system`` asks for the system prompt to be cached. It is a
        request, not a guarantee: below the model's minimum prefix the cache
        silently does not engage, and the only evidence is both cache counters
        returning zero. Implementations must copy those counters across rather
        than assume.
        """

    def complete_as(
        self,
        schema: type[T],
        *,
        model: str,
        system: str,
        prompt: str,
        max_tokens: int,
        cache_system: bool = False,
    ) -> tuple[T, Completion]:
        """Answer into a closed shape, or raise.

        Returns the parsed model and the raw completion, because the caller
        needs the token usage as much as the content.
        """
        completion = self.complete(
            model=model,
            system=system,
            prompt=prompt,
            max_tokens=max_tokens,
            cache_system=cache_system,
        )

        payload = extract_json(completion.text)
        try:
            parsed = schema.model_validate_json(payload)
        except ValidationError as error:
            raise MalformedOutputError(
                f"{self.name} returned an answer that does not fit "
                f"{schema.__name__}: {error.error_count()} problem(s). "
                f"Truncated: {completion.truncated}."
            ) from error
        except json.JSONDecodeError as error:
            raise MalformedOutputError(
                f"{self.name} returned something that is not JSON. "
                f"Truncated: {completion.truncated}."
            ) from error

        return parsed, completion
