"""Unit tests for the cz-linear plugin."""

from __future__ import annotations

from typing import Any, cast
from unittest.mock import MagicMock, PropertyMock, patch

import pytest
from commitizen import git

from cz_linear.cz_linear import LinearCz
from cz_linear.validators import validate_issue_id


@pytest.fixture
def cz_linear() -> LinearCz:
    """Create a LinearCz instance for testing.

    Returns
    -------
    LinearCz
        Configured LinearCz instance
    """
    # Mock the BaseConfig
    config = MagicMock()
    config.settings = {}
    return LinearCz(config)


@pytest.fixture
def mock_commit() -> git.GitCommit:
    """Create a mock commit object.

    Returns
    -------
    git.GitCommit
        Mock commit with message attribute
    """
    commit = MagicMock(spec=git.GitCommit)
    # Use PropertyMock for the message property to allow assignment
    type(commit).message = PropertyMock(return_value="")
    return cast(git.GitCommit, commit)


class TestLinearCz:
    """Test cases for LinearCz plugin."""

    def test_validate_issue_id_valid(self, cz_linear: LinearCz) -> None:
        """Test validation of valid issue IDs."""
        valid_ids = [
            "ENG-123",
            "BUG-1",
            "OPS-9999",
            "PROJ-42",
            "AB-123",
            "ABC-123",
        ]

        for issue_id in valid_ids:
            assert validate_issue_id(issue_id) is True
            # Test case insensitivity
            assert validate_issue_id(issue_id.lower()) is True

    def test_validate_issue_id_invalid(self, cz_linear: LinearCz) -> None:
        """Test validation of invalid issue IDs."""
        invalid_ids = [
            "E-123",  # Too short prefix
            "ENG123",  # Missing dash
            "ENG-",  # Missing number
            "123-ENG",  # Wrong order
            "eng-abc",  # Letters instead of numbers
            "",  # Empty
            "ENG--123",  # Double dash
        ]

        for issue_id in invalid_ids:
            assert validate_issue_id(issue_id) is False

    def test_get_increment_from_commit_major(self, cz_linear: LinearCz) -> None:
        """Test major version increment detection."""
        messages = [
            "ENG-123 Change API response format",
            "BUG-456 Change database schema",
        ]

        for message in messages:
            increment = cz_linear.parser.get_increment_from_message(message)
            assert increment == "MAJOR"

    def test_get_increment_from_commit_minor(self, cz_linear: LinearCz) -> None:
        """Test minor version increment detection."""
        messages = [
            "ENG-123 Add user authentication",
            "BUG-456 Create new dashboard component",
            "OPS-789 Enhance monitoring capabilities",
            "DEV-012 Implement OAuth2 support",
        ]

        for message in messages:
            increment = cz_linear.parser.get_increment_from_message(message)
            assert increment == "MINOR"

    def test_get_increment_from_commit_patch(self, cz_linear: LinearCz) -> None:
        """Test patch version increment detection."""
        messages = [
            "ENG-123 Fix login bug",
            "BUG-456 Update dependencies",
            "OPS-789 Improve performance",
            "DEV-012 Refactor authentication module",
        ]

        for message in messages:
            increment = cz_linear.parser.get_increment_from_message(message)
            assert increment == "PATCH"

    def test_check_manual_bump(self, cz_linear: LinearCz) -> None:
        """Test manual bump override detection."""
        test_cases = [
            ("ENG-123 Fix bug\n\n[bump:major]", "MAJOR"),
            ("ENG-123 Fix bug\n\n[bump:minor]", "MINOR"),
            ("ENG-123 Fix bug\n\n[bump:patch]", "PATCH"),
            ("ENG-123 Fix bug\n\n[BUMP:MAJOR]", "MAJOR"),  # Case insensitive
            ("ENG-123 Fix bug", None),  # No override
        ]

        for message, expected in test_cases:
            result = cz_linear.parser.extract_manual_bump(message)
            assert result == expected

    def test_check_manual_bump_none(self, cz_linear: LinearCz) -> None:
        """Test manual bump override with none."""
        test_cases = [
            ("ENG-123 Fix bug\n\n[bump:none]", None),
            ("ENG-123 Fix bug\n\n[BUMP:NONE]", None),  # Case insensitive
            ("ENG-123 Fix bug\n\n[bump:None]", None),  # Mixed case
        ]

        for message, expected in test_cases:
            result = cz_linear.parser.extract_manual_bump(message)
            assert result == expected

    def test_determine_highest_increment(self, cz_linear: LinearCz) -> None:
        """Test determination of highest increment."""
        test_cases = [
            (["PATCH", "MINOR", "MAJOR"], "MAJOR"),
            (["PATCH", "MINOR"], "MINOR"),
            (["PATCH", "PATCH"], "PATCH"),
            ([], None),
            (["INVALID"], None),
        ]

        for increments, expected in test_cases:
            result = cz_linear._determine_highest_increment(increments)
            assert result == expected

    def test_get_increment_with_manual_override(
        self, cz_linear: LinearCz, mock_commit: git.GitCommit
    ) -> None:
        """Test version increment with manual override."""
        # Patch the 'message' property on the mock's type for this test only
        with patch.object(
            type(mock_commit),
            "message",
            new_callable=PropertyMock,
            return_value="ENG-123 Fix minor bug\n\n[bump:major]",
        ):
            commits = [mock_commit]
            increment = cz_linear.get_increment(commits)
            assert increment == "MAJOR"

    def test_message_generation(self, cz_linear: LinearCz) -> None:
        """Test commit message generation from answers."""
        answers = {
            "issue_id": "eng-123",  # Test uppercase conversion
            "verb": "Fix",
            "description": "authentication bug",
            "body": "This resolves the timeout issue",
        }

        message = cz_linear.message(answers)
        expected = "ENG-123 Fix authentication bug\n\nThis resolves the timeout issue"
        assert message == expected

    def test_message_generation_no_body(self, cz_linear: LinearCz) -> None:
        """Test commit message generation without body."""
        answers = {
            "issue_id": "BUG-456",
            "verb": "Add",
            "description": "new feature",
            "body": "",
        }

        message = cz_linear.message(answers)
        expected = "BUG-456 Add new feature"
        assert message == expected

    def test_changelog_message_builder_hook(
        self, cz_linear: LinearCz, mock_commit: git.GitCommit
    ) -> None:
        """Test changelog message formatting."""
        parsed_message: dict[str, Any] = {
            "issue_id": "ENG-123",
            "message": "Fix authentication bug",
        }

        # The hook is assigned during initialization, so we call it directly
        hook = cz_linear.changelog_message_builder_hook
        assert hook is not None, "Changelog message builder hook should be set"

        result = hook(parsed_message, mock_commit)

        # The hook should return a single dict, not an iterable
        assert isinstance(result, dict)
        result_typed = cast(dict[str, Any], result)
        assert result_typed["message"] == "[ENG-123] Fix authentication bug"

    def test_changelog_message_builder_hook_no_duplicate(
        self, cz_linear: LinearCz, mock_commit: git.GitCommit
    ) -> None:
        """Test changelog formatting doesn't duplicate issue ID."""
        parsed_message: dict[str, Any] = {
            "issue_id": "ENG-123",
            "message": "Fix bug in ENG-123",
        }

        hook = cz_linear.changelog_message_builder_hook
        assert hook is not None, "Changelog message builder hook should be set"

        result = hook(parsed_message, mock_commit)

        # Should always apply the format, even if issue ID is in the message
        assert isinstance(result, dict)
        result_typed = cast(dict[str, Any], result)
        assert result_typed["message"] == "[ENG-123] Fix bug in ENG-123"

    def test_changelog_message_builder_hook_no_issue(
        self, cz_linear: LinearCz, mock_commit: git.GitCommit
    ) -> None:
        """Test changelog formatting when no issue is present."""
        parsed_message: dict[str, Any] = {"message": "Fix authentication bug"}

        hook = cz_linear.changelog_message_builder_hook
        assert hook is not None, "Changelog message builder hook should be set"

        result = hook(parsed_message, mock_commit)

        # Should return message unchanged when no issue
        assert isinstance(result, dict)
        result_typed = cast(dict[str, Any], result)
        assert result_typed["message"] == "Fix authentication bug"

    def test_schema(self, cz_linear: LinearCz) -> None:
        """Test schema output."""
        schema = cz_linear.schema()
        assert "<ISSUE-ID>" in schema
        assert "<Verb>" in schema
        assert "[bump:major|minor|patch|none]" in schema

    def test_info(self, cz_linear: LinearCz) -> None:
        """Test info output."""
        info = cz_linear.info()
        assert "Linear-style" in info
        assert "ENG-123" in info
        assert "Major" in info
        assert "Minor" in info
        assert "Patch" in info

    def test_example(self, cz_linear: LinearCz) -> None:
        """Test example output."""
        example = cz_linear.example()
        assert "ENG-1234" in example
        assert "OPS-567" in example
        assert "[bump:major]" in example
