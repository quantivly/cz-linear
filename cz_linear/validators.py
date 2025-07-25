"""Validation functions for the cz-linear plugin."""

from __future__ import annotations

import re

from .constants import (
    ISSUE_ID_PATTERN,
    MIN_DESCRIPTION_LENGTH,
    VERB_MAP,
)


def validate_issue_id(issue_id: str) -> bool:
    """Validate Linear issue ID format.

    Parameters
    ----------
    issue_id : str
        The issue ID to validate

    Returns
    -------
    bool
        True if valid, False otherwise

    Examples
    --------
    >>> validate_issue_id("ENG-123")
    True
    >>> validate_issue_id("E-123")
    False
    >>> validate_issue_id("eng-123")
    True  # Case insensitive
    """
    return bool(re.match(ISSUE_ID_PATTERN, issue_id.upper().strip()))


def validate_description(description: str) -> bool:
    """Validate commit description.

    Parameters
    ----------
    description : str
        The description to validate

    Returns
    -------
    bool
        True if valid, False otherwise

    Examples
    --------
    >>> validate_description("Fixed bug")
    True
    >>> validate_description("a")
    False
    """
    return len(description.strip()) >= MIN_DESCRIPTION_LENGTH


def validate_verb(verb: str) -> bool:
    """Validate that the verb is in the approved list.

    Parameters
    ----------
    verb : str
        The verb to validate

    Returns
    -------
    bool
        True if valid, False otherwise

    Examples
    --------
    >>> validate_verb("Fixed")
    True
    >>> validate_verb("Fixing")
    False
    """
    return verb in VERB_MAP


def validate_commit_message(message: str) -> tuple[bool, str | None]:
    """Validate the complete commit message format.

    Parameters
    ----------
    message : str
        The complete commit message to validate

    Returns
    -------
    tuple[bool, Optional[str]]
        (is_valid, error_message) - error_message is None if valid

    Examples
    --------
    >>> validate_commit_message("ENG-123 Fixed authentication bug")
    (True, None)
    >>> validate_commit_message("Fixed authentication bug")
    (False, "Invalid format: missing issue ID")
    """
    if not message.strip():
        return False, "Empty commit message"

    lines = message.strip().split("\n")
    first_line = lines[0].strip()
    parts = first_line.split(None, 2)  # Split on whitespace, max 3 parts

    if len(parts) < 3:
        return False, "Invalid format: expected '<ISSUE-ID> <Verb> <description>'"

    issue_id, verb, description = parts[0], parts[1], parts[2]

    if not validate_issue_id(issue_id):
        return False, f"Invalid issue ID format: '{issue_id}'"

    if not validate_verb(verb):
        return False, f"Invalid verb: '{verb}' is not in the approved list"

    if not validate_description(description):
        return (
            False,
            f"Description too short (minimum {MIN_DESCRIPTION_LENGTH} characters)",
        )

    return True, None


def suggest_verb(user_input: str) -> list[str]:
    """Suggest verbs based on partial input.

    Parameters
    ----------
    user_input : str
        Partial verb input from the user

    Returns
    -------
    list[str]
        List of matching verbs

    Examples
    --------
    >>> suggest_verb("fix")
    ['Fixed']
    >>> suggest_verb("add")
    ['Added']
    """
    user_input_lower = user_input.lower()
    return [
        verb for verb in VERB_MAP.keys() if verb.lower().startswith(user_input_lower)
    ]
