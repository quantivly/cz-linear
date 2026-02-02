"""Unit tests for the validators module."""

from __future__ import annotations

from cz_linear.validators import (
    suggest_verb,
    validate_commit_message,
    validate_description,
    validate_issue_id,
    validate_verb,
)


class TestValidators:
    """Test cases for validation functions."""

    def test_validate_issue_id_edge_cases(self) -> None:
        """Test edge cases for issue ID validation."""
        # Minimum valid length
        assert validate_issue_id("AB-1") is True

        # Very long prefix
        assert validate_issue_id("VERYLONGPREFIX-123") is True

        # Leading/trailing whitespace
        assert validate_issue_id("  ENG-123  ") is True

        # Mixed case should be normalized
        assert validate_issue_id("eNg-123") is True

    def test_validate_description_edge_cases(self) -> None:
        """Test edge cases for description validation."""
        # Exactly minimum length
        assert validate_description("abc") is True

        # Just below minimum
        assert validate_description("ab") is False

        # With whitespace
        assert validate_description("  a b c  ") is True
        assert validate_description("   a   ") is False  # Only 1 char after strip

    def test_validate_verb(self) -> None:
        """Test verb validation."""
        # Valid verbs
        assert validate_verb("Fix") is True
        assert validate_verb("Add") is True
        assert validate_verb("Change") is True

        # Invalid verbs
        assert validate_verb("Fixing") is False
        assert validate_verb("fixed") is False  # Case sensitive
        assert validate_verb("Unknown") is False

    def test_validate_commit_message(self) -> None:
        """Test complete commit message validation."""
        # Valid messages
        valid, error = validate_commit_message("ENG-123 Fix authentication bug")
        assert valid is True
        assert error is None

        valid, error = validate_commit_message("BUG-456 Add new feature with spaces")
        assert valid is True
        assert error is None

        # Empty message
        valid, error = validate_commit_message("")
        assert valid is False
        assert "Empty commit message" in error

        # Missing parts
        valid, error = validate_commit_message("ENG-123 Fix")
        assert valid is False
        assert "expected '<ISSUE-ID> <Verb> <description>'" in error

        # Invalid issue ID
        valid, error = validate_commit_message("E-123 Fix bug")
        assert valid is False
        assert "Invalid issue ID format" in error

        # Invalid verb
        valid, error = validate_commit_message("ENG-123 Fixing bug")
        assert valid is False
        assert "Invalid verb" in error

        # Description too short
        valid, error = validate_commit_message("ENG-123 Fix a")
        assert valid is False
        assert "Description too short" in error

    def test_suggest_verb(self) -> None:
        """Test verb suggestion functionality."""
        # Partial matches
        assert "Fix" in suggest_verb("fix")
        assert "Add" in suggest_verb("add")
        assert "Create" in suggest_verb("cre")

        # Multiple matches
        suggestions = suggest_verb("re")
        assert "Refactor" in suggestions
        assert "Release" in suggestions
        assert "Remove" in suggestions
        assert "Resolve" in suggestions
        assert "Revert" in suggestions
        assert "Replace" in suggestions
        assert "Reorganize" in suggestions

        # No matches
        assert suggest_verb("xyz") == []

        # Case insensitive
        assert "Fix" in suggest_verb("FIX")
        assert "Fix" in suggest_verb("Fix")
