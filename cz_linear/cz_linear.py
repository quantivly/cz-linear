"""Linear-style commit convention plugin for Commitizen.

This plugin implements Linear issue tracking conventions for commit messages,
supporting the format: <ISSUE-ID> <Past-tense-verb> <description>
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from typing import Any, cast

from commitizen import git
from commitizen.config.base_config import BaseConfig
from commitizen.cz.base import BaseCommitizen
from commitizen.question import CzQuestion

# Define priority mapping for version increments
INCREMENT_PRIORITY = {
    "MAJOR": 3,
    "MINOR": 2,
    "PATCH": 1,
    "NONE": 0,
}


class LinearCz(BaseCommitizen):
    """Commitizen plugin for Linear-style commit conventions.

    This plugin enforces and parses commit messages in the Linear format:
    <ISSUE-ID> <Past-tense-verb> <description>

    Example: ENG-1234 Fixed authentication bug in login flow
    """

    # Verb mappings for version bumping
    VERB_MAP: dict[str, str] = {
        # Major version bumps (breaking changes)
        "Changed": "MAJOR",
        # Minor version bumps (new features)
        "Added": "MINOR",
        "Created": "MINOR",
        "Enhanced": "MINOR",
        "Implemented": "MINOR",
        # Patch version bumps (bug fixes & maintenance)
        "Bumped": "PATCH",
        "Configured": "PATCH",
        "Deprecated": "PATCH",
        "Disabled": "PATCH",
        "Downgraded": "PATCH",
        "Enabled": "PATCH",
        "Fixed": "PATCH",
        "Improved": "PATCH",
        "Integrated": "PATCH",
        "Merged": "PATCH",
        "Migrated": "PATCH",
        "Optimized": "PATCH",
        "Refactored": "PATCH",
        "Released": "PATCH",
        "Removed": "PATCH",
        "Resolved": "PATCH",
        "Reverted": "PATCH",
        "Tested": "PATCH",
        "Updated": "PATCH",
        "Upgraded": "PATCH",
        "Validated": "PATCH",
        # No version impact
        "Commented": "NONE",
        "Documented": "NONE",
        "Formatted": "NONE",
        "Replaced": "NONE",
        "Reorganized": "NONE",
        "Styled": "NONE",
    }

    # Create verb group for pattern
    _verb_group = "|".join(VERB_MAP.keys())

    # Class-level attributes for commitizen bump support
    bump_pattern = rf"^[A-Z]{{2,}}-[0-9]+\s+({_verb_group})"
    bump_map = VERB_MAP.copy()  # Keep uppercase for commitizen
    bump_map_major_version_zero = bump_map  # Use same map for major version zero

    def __init__(self, config: BaseConfig) -> None:
        """Initialize the Linear Commitizen plugin.

        Parameters
        ----------
        config : BaseConfig
            Configuration object from Commitizen
        """
        super().__init__(config)
        self._setup_patterns()
        # Set the changelog message builder hook
        self.changelog_message_builder_hook = self._changelog_message_builder_hook

    def _setup_patterns(self) -> None:
        """Set up regex patterns for parsing and validation."""

        # Pattern for changelog parsing
        self.changelog_pattern = self.bump_pattern

        # Pattern for commit parsing (captures issue ID and message)
        self.commit_parser = r"^(?P<issue>[A-Z]{2,}-[0-9]+)\s+(?P<message>.*)$"

        # Compiled pattern for manual bump hints
        self._manual_bump_pattern = re.compile(
            r"\[bump:(major|minor|patch|none)\]", re.IGNORECASE
        )

        # Compiled pattern for bump detection
        self._bump_regex = re.compile(self.__class__.bump_pattern)

    def questions(self) -> Iterable[CzQuestion]:
        """Interactive questions for creating commits.

        Returns
        -------
        Iterable[CzQuestion]
            List of questions for the commit command
        """
        questions_list: list[CzQuestion] = [
            cast(
                CzQuestion,
                {
                    "type": "input",
                    "name": "issue",
                    "message": "Linear issue ID (e.g., ENG-123):",
                    "filter": lambda x: x.upper().strip(),
                    "validate": self._validate_issue_id,
                },
            ),
            cast(
                CzQuestion,
                {
                    "type": "list",
                    "name": "verb",
                    "message": "Select the type of change:",
                    "choices": self._get_verb_choices(),
                },
            ),
            cast(
                CzQuestion,
                {
                    "type": "input",
                    "name": "description",
                    "message": "Brief description of the change:",
                    "validate": self._validate_description,
                },
            ),
            cast(
                CzQuestion,
                {
                    "type": "input",
                    "name": "body",
                    "message": "Detailed description (optional). Press Enter to skip:",
                },
            ),
        ]
        return questions_list

    def _validate_issue_id(self, issue_id: str) -> bool:
        """Validate Linear issue ID format.

        Parameters
        ----------
        issue_id : str
            The issue ID to validate

        Returns
        -------
        bool
            True if valid, False otherwise
        """
        pattern = r"^[A-Z]{2,}-[0-9]+$"
        return bool(re.match(pattern, issue_id.upper().strip()))

    def _validate_description(self, description: str) -> bool:
        """Validate commit description.

        Parameters
        ----------
        description : str
            The description to validate

        Returns
        -------
        bool
            True if valid, False otherwise
        """
        return len(description.strip()) >= 3

    def _get_verb_choices(self) -> list[dict[str, Any]]:
        """Get verb choices organized by version impact.

        Returns
        -------
        list[dict[str, Any]]
            List of choice dictionaries for the questionary prompt
        """
        choices = []

        # Group verbs by their version impact
        major_verbs = [v for v, t in self.VERB_MAP.items() if t == "MAJOR"]
        minor_verbs = [v for v, t in self.VERB_MAP.items() if t == "MINOR"]
        patch_verbs = [v for v, t in self.VERB_MAP.items() if t == "PATCH"]
        none_verbs = [v for v, t in self.VERB_MAP.items() if t == "NONE"]

        # Add section headers and choices
        if major_verbs:
            choices.append(
                {"name": "── Breaking Changes (Major) ──", "disabled": "section"}
            )
            choices.extend(
                {"name": f"{verb} - Breaking change", "value": verb}
                for verb in sorted(major_verbs)
            )

        if minor_verbs:
            choices.append(
                {"name": "── New Features (Minor) ──", "disabled": "section"}
            )
            choices.extend(
                {"name": f"{verb} - New feature/capability", "value": verb}
                for verb in sorted(minor_verbs)
            )

        if patch_verbs:
            choices.append(
                {"name": "── Fixes & Maintenance (Patch) ──", "disabled": "section"}
            )
            choices.extend(
                {"name": f"{verb} - Bug fix/improvement", "value": verb}
                for verb in sorted(patch_verbs)
            )
        if none_verbs:
            choices.append({"name": "── Other Changes ──", "disabled": "section"})
            choices.extend(
                {"name": f"{verb} - No version impact", "value": verb}
                for verb in sorted(none_verbs)
            )

        return choices

    def message(self, answers: Mapping[str, Any]) -> str:
        """Generate commit message from answers.

        Parameters
        ----------
        answers : Mapping[str, Any]
            Answers from the interactive prompt

        Returns
        -------
        str
            Formatted commit message
        """
        issue = answers["issue"].upper().strip()
        verb = answers["verb"]
        description = answers["description"].strip()
        body = answers.get("body", "").strip()

        message = f"{issue} {verb} {description}"

        if body:
            message += f"\n\n{body}"

        return message

    def example(self) -> str:
        """Provide example commit messages.

        Returns
        -------
        str
            Example commit messages
        """
        return (
            "ENG-1234 Fixed authentication bug in login flow\n"
            "OPS-567 Added monitoring dashboard for API endpoints\n"
            "BUG-890 Changed database schema to support multi-tenancy\n"
            "\n"
            "With manual bump:\n"
            "ENG-999 Updated config handling\n"
            "\n"
            "This change requires a major version bump due to config format changes.\n"
            "[bump:major]"
        )

    def schema(self) -> str:
        """Show the expected commit format.

        Returns
        -------
        str
            Schema description
        """
        return (
            "<ISSUE-ID> <Verb> <description>\n"
            "\n"
            "[optional body]\n"
            "\n"
            "[bump:major|minor|patch|none] (optional)"
        )

    def info(self) -> str:
        """Provide information about the commit rules.

        Returns
        -------
        str
            Detailed information about the convention
        """
        return (
            "Linear-style commit format:\n"
            "\n"
            "Format: <ISSUE-ID> <Past-tense-verb> <description>\n"
            "Example: ENG-1234 Fixed authentication bug\n"
            "\n"
            "Issue ID format: 2+ uppercase letters, dash, number (e.g., ENG-123)\n"
            "\n"
            "Version bumping:\n"
            "- Major (breaking): Changed\n"
            "- Minor (features): Added, Created, Enhanced, Implemented\n"
            "- Patch (fixes): Fixed, Updated, Improved, etc.\n"
            "\n"
            "Manual bump override: Add [bump:major], [bump:minor], [bump:patch],\n"
            "or [bump:none] to the commit body to override automatic detection."
        )

    def get_increment(self, commits: list[git.GitCommit]) -> str | None:
        """Determine version increment from commits.

        Parameters
        ----------
        commits : list[git.GitCommit]
            List of commits to analyze

        Returns
        -------
        str | None
            "MAJOR", "MINOR", "PATCH", or None
        """
        if not commits:
            return None

        # Check for manual bump overrides first
        for commit in commits:
            increment = self._check_manual_bump(commit.message)
            if increment:
                return increment

        # Use standard pattern matching
        increments = []
        for commit in commits:
            increment = self._get_increment_from_commit(commit.message)
            if increment:
                increments.append(increment)

        return self._determine_highest_increment(increments)

    def _check_manual_bump(self, message: str) -> str | None:
        """Check for manual bump hints in commit message.

        Parameters
        ----------
        message : str
            Commit message to check

        Returns
        -------
        str | None
            "MAJOR", "MINOR", "PATCH", or None
        """
        match = self._manual_bump_pattern.search(message)
        if match:
            increment = match.group(1).upper()
            return increment if increment != "NONE" else None
        return None

    def _get_increment_from_commit(self, message: str) -> str | None:
        """Extract version increment from a single commit.

        Parameters
        ----------
        message : str
            Commit message to analyze

        Returns
        -------
        str | None
            "MAJOR", "MINOR", "PATCH", or None
        """
        # Extract first line for verb parsing
        first_line = message.split("\n")[0]

        # Try to match the pattern and extract verb
        match = self._bump_regex.match(first_line)
        if match:
            verb = match.group(1)
            return self.VERB_MAP.get(verb)

        return None

    def _determine_highest_increment(self, increments: list[str]) -> str | None:
        """Determine the highest increment from a list.

        Parameters
        ----------
        increments : list[str]
            List of increment types

        Returns
        -------
        str | None
            The highest increment type or None
        """
        if not increments:
            return None

        increments_with_priority = [
            (INCREMENT_PRIORITY.get(inc, 0), inc) for inc in increments
        ]
        highest = max(increments_with_priority, key=lambda x: x[0])

        return highest[1] if highest[0] > 0 else None

    def _changelog_message_builder_hook(
        self, message: dict[str, Any], commit: git.GitCommit
    ) -> dict[str, Any]:
        """Format messages for changelog generation.

        Parameters
        ----------
        message : dict[str, Any]
            Parsed commit message data
        commit : git.GitCommit
            The commit object

        Returns
        -------
        dict[str, Any]
            Modified message data for changelog
        """
        # If we have an issue ID, append it to the message
        if "issue" in message:
            original_msg = message.get("message", "")
            issue_id = message["issue"]

            # Check if issue ID is already in the message
            if issue_id not in original_msg:
                message["message"] = f"{original_msg} ({issue_id})"

        return message


# Expose the class for the plugin system
discover_this = LinearCz
