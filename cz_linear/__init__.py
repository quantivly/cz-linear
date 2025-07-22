"""Linear-style commit convention plugin for Commitizen.

A Commitizen plugin that implements Linear issue tracking conventions,
supporting commit messages in the format: <ISSUE-ID> <Past-tense-verb> <description>
"""

from __future__ import annotations

__version__ = "1.0.0"

def __getattr__(name):
    """Lazy import to avoid circular import issues."""
    if name == "LinearCz":
        from .cz_linear import LinearCz
        return LinearCz
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
