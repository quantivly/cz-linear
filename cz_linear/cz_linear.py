"""Linear-style commit convention plugin for Commitizen.

This plugin implements Linear issue tracking conventions for commit messages,
supporting the format: <ISSUE-ID> <Imperative-verb> <description>
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from commitizen import git
from commitizen.config.base_config import BaseConfig
from commitizen.cz.base import BaseCommitizen

try:
    from commitizen.question import CzQuestion
except ImportError:
    # For older versions of commitizen or different environments
    CzQuestion = dict[str, Any]

from .constants import (
    CHANGELOG_MESSAGE_FORMAT,
    INCREMENT_PRIORITY,
    PROMPT_BODY,
    PROMPT_DESCRIPTION,
    PROMPT_ISSUE_ID,
    PROMPT_VERB,
    SECTION_MAJOR,
    SECTION_MINOR,
    SECTION_NONE,
    SECTION_PATCH,
    VERB_DESC_MAJOR,
    VERB_DESC_MINOR,
    VERB_DESC_NONE,
    VERB_DESC_PATCH,
    VERB_MAP,
)
from .parser import CommitParser
from .validators import validate_description, validate_issue_id


class LinearCz(BaseCommitizen):
    """Commitizen plugin for Linear-style commit conventions.

    This plugin enforces and parses commit messages in the Linear format:
    <ISSUE-ID> <Imperative-verb> <description>

    Example: ENG-1234 Fix authentication bug in login flow
    """

    # Create verb group for pattern
    _verb_group = "|".join(VERB_MAP.keys())

    # Class-level attributes for commitizen bump support
    bump_pattern = rf"^[A-Z]{{2,}}-[0-9]+\s+({_verb_group})\b"
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
        self.parser = CommitParser()
        self._setup_patterns()
        # Set the changelog message builder hook
        self.changelog_message_builder_hook = self._changelog_message_builder_hook

    def _setup_patterns(self) -> None:
        """Set up regex patterns for parsing and validation."""
        # Pattern for changelog parsing
        self.changelog_pattern = self.bump_pattern
        # Pattern for commit parsing (captures issue ID and message)
        self.commit_parser = self.parser.commit_pattern.pattern

    def questions(self) -> list[CzQuestion]:
        """Interactive questions for creating commits.

        Returns
        -------
        list[CzQuestion]
            List of questions for the commit command
        """
        questions_list: list[CzQuestion] = [
            cast(
                CzQuestion,
                {
                    "type": "input",
                    "name": "issue_id",
                    "message": PROMPT_ISSUE_ID,
                    "filter": lambda x: x.upper().strip(),
                    "validate": validate_issue_id,
                },
            ),
            cast(
                CzQuestion,
                {
                    "type": "list",
                    "name": "verb",
                    "message": PROMPT_VERB,
                    "choices": self._get_verb_choices(),
                },
            ),
            cast(
                CzQuestion,
                {
                    "type": "input",
                    "name": "description",
                    "message": PROMPT_DESCRIPTION,
                    "validate": validate_description,
                },
            ),
            cast(
                CzQuestion,
                {
                    "type": "input",
                    "name": "body",
                    "message": PROMPT_BODY,
                },
            ),
        ]
        return questions_list

    def _get_verb_choices(self) -> list[dict[str, Any]]:
        """Get verb choices organized by version impact.

        Returns
        -------
        list[dict[str, Any]]
            List of choice dictionaries for the questionary prompt
        """
        choices = []

        # Group verbs by their version impact
        major_verbs = [v for v, t in VERB_MAP.items() if t == "MAJOR"]
        minor_verbs = [v for v, t in VERB_MAP.items() if t == "MINOR"]
        patch_verbs = [v for v, t in VERB_MAP.items() if t == "PATCH"]
        none_verbs = [v for v, t in VERB_MAP.items() if t == "NONE"]

        # Add section headers and choices
        if major_verbs:
            choices.append({"name": SECTION_MAJOR, "disabled": "section"})
            choices.extend(
                {"name": f"{verb} - {VERB_DESC_MAJOR}", "value": verb}
                for verb in sorted(major_verbs)
            )

        if minor_verbs:
            choices.append({"name": SECTION_MINOR, "disabled": "section"})
            choices.extend(
                {"name": f"{verb} - {VERB_DESC_MINOR}", "value": verb}
                for verb in sorted(minor_verbs)
            )

        if patch_verbs:
            choices.append({"name": SECTION_PATCH, "disabled": "section"})
            choices.extend(
                {"name": f"{verb} - {VERB_DESC_PATCH}", "value": verb}
                for verb in sorted(patch_verbs)
            )
        if none_verbs:
            choices.append({"name": SECTION_NONE, "disabled": "section"})
            choices.extend(
                {"name": f"{verb} - {VERB_DESC_NONE}", "value": verb}
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
        issue_id = answers["issue_id"].upper().strip()
        verb = answers["verb"]
        description = answers["description"].strip()
        body = answers.get("body", "").strip()

        message = f"{issue_id} {verb} {description}"

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
            "ENG-1234 Fix authentication bug in login flow\n"
            "OPS-567 Add monitoring dashboard for API endpoints\n"
            "BUG-890 Change database schema to support multi-tenancy\n"
            "\n"
            "With manual bump:\n"
            "ENG-999 Update config handling\n"
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

    def schema_pattern(self) -> str:
        """Return the regex pattern for the commit schema.

        Returns
        -------
        str
            Regex pattern for commit validation
        """
        return self.bump_pattern

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
            "Format: <ISSUE-ID> <Imperative-verb> <description>\n"
            "Example: ENG-1234 Fix authentication bug\n"
            "\n"
            "Issue ID format: 2+ uppercase letters, dash, number (e.g., ENG-123)\n"
            "\n"
            "Version bumping:\n"
            "- Major (breaking): Change\n"
            "- Minor (features): Add, Create, Enhance, Implement\n"
            "- Patch (fixes): Fix, Update, Improve, etc.\n"
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
            increment = self.parser.extract_manual_bump(commit.message)
            if increment:
                return increment

        # Use standard pattern matching
        increments = []
        for commit in commits:
            increment = self.parser.get_increment_from_message(commit.message)
            if increment:
                increments.append(increment)

        return self._determine_highest_increment(increments)

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
        # If we have an issue ID, format according to CHANGELOG_MESSAGE_FORMAT
        if "issue_id" in message:
            original_msg = message.get("message", "")
            issue_id = message["issue_id"]

            # Apply the format: [{issue_id}] {message}
            message["message"] = CHANGELOG_MESSAGE_FORMAT.format(
                issue_id=issue_id, message=original_msg
            )

        return message


# Expose the class for the plugin system
discover_this = LinearCz
