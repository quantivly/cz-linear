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
        assert validate_verb("Fixed") is True
        assert validate_verb("Added") is True
        assert validate_verb("Changed") is True

        # Invalid verbs
        assert validate_verb("Fixing") is False
        assert validate_verb("fixed") is False  # Case sensitive
        assert validate_verb("Unknown") is False

    def test_validate_commit_message(self) -> None:
        """Test complete commit message validation."""
        # Valid messages
        valid, error = validate_commit_message("ENG-123 Fixed authentication bug")
        assert valid is True
        assert error is None

        valid, error = validate_commit_message("BUG-456 Added new feature with spaces")
        assert valid is True
        assert error is None

        # Empty message
        valid, error = validate_commit_message("")
        assert valid is False
        assert "Empty commit message" in error

        # Missing parts
        valid, error = validate_commit_message("ENG-123 Fixed")
        assert valid is False
        assert "expected '<ISSUE-ID> <Verb> <description>'" in error

        # Invalid issue ID
        valid, error = validate_commit_message("E-123 Fixed bug")
        assert valid is False
        assert "Invalid issue ID format" in error

        # Invalid verb
        valid, error = validate_commit_message("ENG-123 Fixing bug")
        assert valid is False
        assert "Invalid verb" in error

        # Description too short
        valid, error = validate_commit_message("ENG-123 Fixed a")
        assert valid is False
        assert "Description too short" in error

    def test_suggest_verb(self) -> None:
        """Test verb suggestion functionality."""
        # Partial matches
        assert "Fixed" in suggest_verb("fix")
        assert "Added" in suggest_verb("add")
        assert "Created" in suggest_verb("cre")

        # Multiple matches
        suggestions = suggest_verb("re")
        assert "Refactored" in suggestions
        assert "Released" in suggestions
        assert "Removed" in suggestions
        assert "Resolved" in suggestions
        assert "Reverted" in suggestions
        assert "Replaced" in suggestions
        assert "Reorganized" in suggestions

        # No matches
        assert suggest_verb("xyz") == []

        # Case insensitive
        assert "Fixed" in suggest_verb("FIX")
        assert "Fixed" in suggest_verb("Fix")
