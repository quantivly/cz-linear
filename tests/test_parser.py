"""Unit tests for the parser module."""

from __future__ import annotations

import pytest

from cz_linear.parser import CommitParser


class TestCommitParser:
    """Test cases for CommitParser class."""

    @pytest.fixture
    def parser(self) -> CommitParser:
        """Create a CommitParser instance for testing."""
        return CommitParser()

    def test_parse_commit_valid(self, parser: CommitParser) -> None:
        """Test parsing valid commit messages."""
        # Simple commit
        result = parser.parse_commit("ENG-123 Fixed authentication bug")
        assert result["issue_id"] == "ENG-123"
        assert result["verb"] == "Fixed"
        assert result["description"] == "authentication bug"
        assert result["body"] == ""
        assert result["manual_bump"] is None

        # With body
        result = parser.parse_commit("BUG-456 Added new feature\n\nThis is the body")
        assert result["issue_id"] == "BUG-456"
        assert result["verb"] == "Added"
        assert result["description"] == "new feature"
        assert result["body"] == "This is the body"

        # With manual bump
        result = parser.parse_commit("OPS-789 Updated dependencies\n\n[bump:major]")
        assert result["issue_id"] == "OPS-789"
        assert result["verb"] == "Updated"
        assert result["manual_bump"] == "MAJOR"

    def test_parse_commit_invalid(self, parser: CommitParser) -> None:
        """Test parsing invalid commit messages."""
        # No issue ID
        result = parser.parse_commit("Fixed authentication bug")
        assert result["issue_id"] is None
        assert result["verb"] is None
        assert result["description"] == "Fixed authentication bug"

        # Invalid verb
        result = parser.parse_commit("ENG-123 Fixing authentication bug")
        assert result["issue_id"] == "ENG-123"
        assert result["verb"] is None
        assert result["description"] == "Fixing authentication bug"

        # Only issue ID (no space after, so doesn't match pattern)
        result = parser.parse_commit("ENG-123")
        assert result["issue_id"] is None
        assert result["verb"] is None
        assert result["description"] == "ENG-123"

    def test_extract_manual_bump(self, parser: CommitParser) -> None:
        """Test manual bump extraction."""
        # Various formats
        assert parser.extract_manual_bump("[bump:major]") == "MAJOR"
        assert parser.extract_manual_bump("[bump:minor]") == "MINOR"
        assert parser.extract_manual_bump("[bump:patch]") == "PATCH"
        assert parser.extract_manual_bump("[bump:none]") is None

        # Case insensitive
        assert parser.extract_manual_bump("[BUMP:MAJOR]") == "MAJOR"
        assert parser.extract_manual_bump("[Bump:Minor]") == "MINOR"

        # In context
        message = "ENG-123 Fixed bug\n\nSome description\n[bump:major]"
        assert parser.extract_manual_bump(message) == "MAJOR"

        # No bump
        assert parser.extract_manual_bump("ENG-123 Fixed bug") is None

    def test_extract_verb_from_first_line(self, parser: CommitParser) -> None:
        """Test verb extraction from first line."""
        assert parser.extract_verb_from_first_line("ENG-123 Fixed bug") == "Fixed"
        assert parser.extract_verb_from_first_line("BUG-456 Added feature") == "Added"
        assert parser.extract_verb_from_first_line("OPS-789 Fixing bug") is None
        assert parser.extract_verb_from_first_line("No issue ID here") is None

    def test_get_increment_from_message(self, parser: CommitParser) -> None:
        """Test version increment detection."""
        # From verb
        assert parser.get_increment_from_message("ENG-123 Fixed bug") == "PATCH"
        assert parser.get_increment_from_message("ENG-123 Added feature") == "MINOR"
        assert parser.get_increment_from_message("ENG-123 Changed API") == "MAJOR"

        # Manual override takes precedence
        assert (
            parser.get_increment_from_message("ENG-123 Fixed bug\n\n[bump:major]")
            == "MAJOR"
        )

        # No increment
        assert parser.get_increment_from_message("ENG-123 Unknown verb") is None
        assert parser.get_increment_from_message("Invalid format") is None

    def test_parse_commit_edge_cases(self, parser: CommitParser) -> None:
        """Test edge cases in commit parsing."""
        # Extra whitespace
        result = parser.parse_commit("  ENG-123   Fixed   authentication bug  ")
        assert result["issue_id"] == "ENG-123"
        assert result["verb"] == "Fixed"
        assert result["description"] == "authentication bug"

        # Multiple spaces in description
        result = parser.parse_commit("ENG-123 Fixed  multiple   spaces   here")
        assert result["description"] == "multiple   spaces   here"

        # Very long description
        long_desc = "a" * 1000
        result = parser.parse_commit(f"ENG-123 Fixed {long_desc}")
        assert result["description"] == long_desc

        # Empty body lines
        result = parser.parse_commit("ENG-123 Fixed bug\n\n\n\nBody here")
        assert result["body"] == "Body here"
