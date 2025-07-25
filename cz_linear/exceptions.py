"""Custom exceptions for the cz-linear plugin."""

from __future__ import annotations


class CzLinearError(Exception):
    """Base exception for cz-linear plugin errors."""

    pass


class ValidationError(CzLinearError):
    """Raised when validation fails."""

    def __init__(self, message: str, field: str | None = None) -> None:
        """Initialize validation error.

        Parameters
        ----------
        message : str
            The error message
        field : str | None
            The field that failed validation
        """
        super().__init__(message)
        self.field = field


class ConfigurationError(CzLinearError):
    """Raised when configuration is invalid."""

    pass


class ParseError(CzLinearError):
    """Raised when commit message parsing fails."""

    def __init__(self, message: str, commit_message: str | None = None) -> None:
        """Initialize parse error.

        Parameters
        ----------
        message : str
            The error message
        commit_message : str | None
            The commit message that failed to parse
        """
        super().__init__(message)
        self.commit_message = commit_message
