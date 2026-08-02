"""Model access, behind one interface.

Every call in the project goes through ``LLMProvider``. Project 2 compares two
providers on the same cases; that comparison costs nothing extra only because
nothing outside this package ever imports a vendor SDK.
"""

from arpent.llm.provider import (
    Completion,
    LLMError,
    LLMProvider,
    MalformedOutputError,
    as_data,
)

__all__ = [
    "Completion",
    "LLMError",
    "LLMProvider",
    "MalformedOutputError",
    "as_data",
]
