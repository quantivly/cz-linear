"""Linear-style commit convention plugin for Commitizen.

A Commitizen plugin that implements Linear issue tracking conventions,
supporting commit messages in the format: <ISSUE-ID> <Past-tense-verb> <description>
"""

from __future__ import annotations

from .cz_linear import LinearCz

__version__ = "1.0.0"
__all__ = ["LinearCz"]
