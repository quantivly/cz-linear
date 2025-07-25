# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Commitizen plugin called `cz-linear` that implements Linear issue tracking conventions for commit messages. The plugin enforces the format:

```
<ISSUE-ID> <Past-tense-verb> <description>
```

Example: `ENG-1234 Fixed authentication bug in login flow`

## Development Commands

### Testing
```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=cz_linear
```

### Code Quality
```bash
# Format code
black cz_linear tests

# Lint code
ruff check cz_linear tests

# Type check
mypy cz_linear
```

### Building
```bash
# Build the package
python -m build

# Install in development mode
pip install -e ".[dev]"
```

## Architecture

The codebase follows a simple plugin architecture:

1. **`cz_linear/cz_linear.py`** - Main plugin implementation
   - `LinearCz` class extends `BaseCommitizen` from commitizen
   - Implements commit message validation, version bumping logic, and interactive prompts
   - Maps verbs to version increments (MAJOR/MINOR/PATCH/NONE)
   - Supports manual bump overrides via `[bump:TYPE]` in commit messages

2. **`cz_linear/__init__.py`** - Package initialization
   - Uses lazy import pattern to avoid circular imports
   - Exposes `LinearCz` class

3. **Entry Point** - Registered via `pyproject.toml`
   - Plugin is discoverable by commitizen through `commitizen.plugin` entry point

## Key Implementation Details

### Verb Mapping
The plugin categorizes verbs into version bump types:
- **MAJOR**: "Changed" (breaking changes)
- **MINOR**: "Added", "Created", "Enhanced", "Implemented" (new features)
- **PATCH**: "Fixed", "Updated", "Improved", etc. (bug fixes)
- **NONE**: "Commented", "Documented", "Formatted", etc. (no version impact)

### Version Bumping Logic
1. First checks for manual bump overrides (`[bump:TYPE]`)
2. Falls back to verb-based detection
3. Selects highest increment when multiple commits exist

### Commit Message Validation
- Issue ID: 2+ uppercase letters, dash, number (e.g., `ENG-123`)
- Verb: Must be from the predefined list
- Description: Minimum 3 characters

## Testing Approach

Tests use pytest with mocking for commitizen dependencies. Key test areas:
- Issue ID validation
- Verb-based version increment detection
- Manual bump override handling
- Commit message generation
- Changelog formatting

## Linear Workflow Integration

When working on Linear issues:
- Branch naming: `user/aaa-1234-my-issue-description`
- Commit format: `AAA-1234 <Verb> <description>`
- PR title format: `AAA-#### Summary`