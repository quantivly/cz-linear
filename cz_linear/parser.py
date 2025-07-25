"""Commit message parsing functionality for the cz-linear plugin."""

from __future__ import annotations

import re
from typing import Any

from .constants import COMMIT_PARSER_PATTERN, MANUAL_BUMP_PATTERN, VERB_MAP


class CommitParser:
    """Parser for Linear-style commit messages."""

    def __init__(self) -> None:
        """Initialize the commit parser with compiled regex patterns."""
        self.commit_pattern = re.compile(COMMIT_PARSER_PATTERN)
        self.manual_bump_pattern = re.compile(MANUAL_BUMP_PATTERN, re.IGNORECASE)
        self.verb_pattern = re.compile(
            rf"^[A-Z]{{2,}}-[0-9]+\s+({'|'.join(VERB_MAP.keys())})"
        )

    def parse_commit(self, message: str) -> dict[str, Any]:
        """Parse a commit message into its components.

        Parameters
        ----------
        message : str
            The commit message to parse

        Returns
        -------
        dict[str, Any]
            Parsed components with keys:
            - issue_id: The Linear issue ID
            - verb: The action verb
            - description: The commit description
            - body: Optional commit body
            - manual_bump: Optional manual bump override

        Examples
        --------
        >>> parser = CommitParser()
        >>> result = parser.parse_commit("ENG-123 Fixed authentication bug")
        >>> result["issue_id"]
        'ENG-123'
        >>> result["verb"]
        'Fixed'
        """
        lines = message.strip().split("\n", 1)
        first_line = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else ""

        # Parse the first line
        match = self.commit_pattern.match(first_line)
        if not match:
            return {
                "issue_id": None,
                "verb": None,
                "description": first_line,
                "body": body,
                "manual_bump": self.extract_manual_bump(message),
            }

        issue_id = match.group("issue_id")
        remaining = match.group("message").strip()

        # Extract verb from remaining message
        parts = remaining.split(None, 1)
        verb = parts[0] if parts else None
        description = parts[1] if len(parts) > 1 else ""

        # Validate verb
        if verb not in VERB_MAP:
            verb = None
            description = remaining

        return {
            "issue_id": issue_id,
            "verb": verb,
            "description": description,
            "body": body,
            "manual_bump": self.extract_manual_bump(message),
        }

    def extract_manual_bump(self, message: str) -> str | None:
        """Extract manual bump override from commit message.

        Parameters
        ----------
        message : str
            The commit message to check

        Returns
        -------
        Optional[str]
            "MAJOR", "MINOR", "PATCH", or None

        Examples
        --------
        >>> parser = CommitParser()
        >>> parser.extract_manual_bump("ENG-123 Fixed bug\\n\\n[bump:major]")
        'MAJOR'
        """
        match = self.manual_bump_pattern.search(message)
        if match:
            increment = match.group(1).upper()
            return increment if increment != "NONE" else None
        return None

    def extract_verb_from_first_line(self, first_line: str) -> str | None:
        """Extract the verb from the first line of a commit.

        Parameters
        ----------
        first_line : str
            The first line of the commit message

        Returns
        -------
        Optional[str]
            The verb if found and valid, None otherwise
        """
        match = self.verb_pattern.match(first_line)
        if match:
            return match.group(1)
        return None

    def get_increment_from_message(self, message: str) -> str | None:
        """Get the version increment from a commit message.

        Parameters
        ----------
        message : str
            The commit message to analyze

        Returns
        -------
        Optional[str]
            "MAJOR", "MINOR", "PATCH", or None
        """
        # Check for manual bump first
        manual_bump = self.extract_manual_bump(message)
        if manual_bump:
            return manual_bump

        # Extract verb and determine increment
        first_line = message.split("\n")[0]
        verb = self.extract_verb_from_first_line(first_line)
        if verb:
            return VERB_MAP.get(verb)

        return None
