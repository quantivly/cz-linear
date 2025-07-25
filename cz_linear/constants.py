"""Constants and mappings for the cz-linear plugin."""

from __future__ import annotations

# Version increment priority mapping
INCREMENT_PRIORITY: dict[str, int] = {
    "MAJOR": 3,
    "MINOR": 2,
    "PATCH": 1,
    "NONE": 0,
}

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

# Regex patterns
ISSUE_ID_PATTERN = r"^[A-Z]{2,}-[0-9]+$"
COMMIT_PARSER_PATTERN = r"^(?P<issue_id>[A-Z]{2,}-[0-9]+)\s+(?P<message>.*)$"
MANUAL_BUMP_PATTERN = r"\[bump:(major|minor|patch|none)\]"

# Changelog formatting
CHANGELOG_MESSAGE_FORMAT = "[{issue_id}] {message}"

# Validation constraints
MIN_DESCRIPTION_LENGTH = 3
MIN_ISSUE_PREFIX_LENGTH = 2

# Interactive prompt messages
PROMPT_ISSUE_ID = "Linear issue ID (e.g., ENG-123):"
PROMPT_VERB = "Select the type of change:"
PROMPT_DESCRIPTION = "Brief description of the change:"
PROMPT_BODY = "Detailed description (optional). Press Enter to skip:"

# Section headers for verb choices
SECTION_MAJOR = "── Breaking Changes (Major) ──"
SECTION_MINOR = "── New Features (Minor) ──"
SECTION_PATCH = "── Fixes & Maintenance (Patch) ──"
SECTION_NONE = "── Other Changes ──"

# Verb descriptions
VERB_DESC_MAJOR = "Breaking change"
VERB_DESC_MINOR = "New feature/capability"
VERB_DESC_PATCH = "Bug fix/improvement"
VERB_DESC_NONE = "No version impact"
