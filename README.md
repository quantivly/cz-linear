# cz-linear

A [Commitizen](https://commitizen-tools.github.io/commitizen/) plugin that implements
Linear issue tracking conventions for commit messages.

## Overview

This plugin enforces the Linear commit message format:

```sh
<ISSUE-ID> <Past-tense-verb> <description>
```

Example:

```sh
ENG-1234 Fixed authentication bug in login flow
```

## Features

- **Automatic version bumping** based on commit verbs (major/minor/patch)
- **Interactive commit creation** with guided prompts
- **Linear issue ID validation** (e.g., ENG-123, TEA-456)
- **Manual bump overrides** using `[bump:TYPE]` in commit messages
- **Changelog generation** with Linear issue references
- **Pre-commit hook support** for commit message validation
- **Customizable verb mappings** (custom verbs take precedence over built-in ones)
- **Configurable issue patterns** for different tracking systems

## Installation

### Requirements

- Python 3.9 or higher
- Git

### Install from PyPI

```bash
pip install cz-linear
```

Or with [pipx](https://pipx.pypa.io/) for isolated installation:

```bash
pipx install commitizen
pipx inject commitizen cz-linear
```

## Configuration

Add to your `pyproject.toml`:

```toml
[tool.commitizen]
name = "cz_linear"
version = "0.1.0"
tag_format = "v$version"
version_files = [
    "pyproject.toml:version"
]
```

Or in `.cz.toml`:

```toml
[commitizen]
name = "cz_linear"
version = "0.1.0"
tag_format = "v$version"
version_files = [
    "pyproject.toml:version"
]
```

### Advanced Configuration

```toml
[tool.commitizen]
name = "cz_linear"

# Custom verb mappings (these take precedence over built-in verbs)
[tool.commitizen.cz_linear]
custom_verbs = {
    "Deployed" = "PATCH",      # Adds new verb
    "Changed" = "MINOR",       # Overrides built-in (normally MAJOR)
    "Archived" = "NONE"        # No version bump
}

# Custom issue pattern (default: Linear format)
# GitHub style: #123
issue_pattern = "^#[0-9]+$"

# JIRA style: PROJ-123
# issue_pattern = "^[A-Z]+-[0-9]+$"

# Custom format: TASK-2023-001
# issue_pattern = "^TASK-[0-9]{4}-[0-9]{3}$"
```

## Usage

### Interactive Commit

Create commits interactively:

```bash
cz commit
```

You'll be prompted for:

1. Linear issue ID (e.g., ENG-123)
2. Type of change (verb)
3. Brief description
4. Optional detailed description

Example session:

```sh
$ cz commit

Linear issue ID (e.g., ENG-123): ENG-456
Select the type of change:
  ── New Features (Minor) ──
> Added - New feature/capability
  Created - New feature/capability
  Enhanced - New feature/capability

Brief description of the change: user authentication with OAuth
Detailed description (optional). Press Enter to skip:

This adds support for GitHub and Google OAuth providers.

[master 1a2b3c4] ENG-456 Added user authentication with OAuth
```

### Version Bumping

Automatically determine version bump from commits:

```bash
cz bump
```

With changelog generation:

```bash
cz bump --changelog
```

Dry run to preview changes:

```bash
cz bump --dry-run
```

### Manual Version Override

Include `[bump:TYPE]` in your commit message to override automatic detection:

```sh
ENG-999 Updated configuration handling

This change modifies the config format and breaks backward compatibility.
[bump:major]
```

## Verb Mappings

The plugin maps commit verbs to version increments:

### Major Version (Breaking Changes)

- `Changed` - Indicates breaking changes

### Minor Version (New Features)

- `Added` - New features or capabilities
- `Created` - New components or resources
- `Enhanced` - Significant improvements
- `Implemented` - New implementations

### Patch Version (Bug Fixes & Maintenance)

- `Fixed` - Bug fixes
- `Updated` - Dependency or documentation updates
- `Improved` - Performance or quality improvements
- `Refactored` - Code refactoring
- `Bumped`, `Configured`, `Deprecated`, `Disabled`, `Downgraded`
- `Enabled`, `Integrated`, `Merged`, `Migrated`, `Optimized`
- `Released`, `Removed`, `Resolved`, `Reverted`, `Tested`
- `Upgraded`, `Validated`

### No Version Impact

- `Commented` - Code comments
- `Documented` - Documentation changes
- `Formatted` - Code formatting
- `Replaced` - Simple replacements
- `Reorganized` - File/folder reorganization
- `Styled` - Style changes

## Commit Message Format

### Structure

```sh
<ISSUE-ID> <Verb> <description>

[optional body]

[bump:major|minor|patch] (optional)
```

### Rules

- **Issue ID**: 2+ uppercase letters, dash, number (e.g., `ENG-123`, `PROJ-4567`)
- **Verb**: Past-tense verb from the approved list
- **Description**: Brief summary of the change (minimum 3 characters)
- **Body**: Optional detailed explanation
- **Manual bump**: Optional override for version detection

### Examples

Basic commit:

```sh
BUG-123 Fixed null pointer exception in user service
```

With body:

```sh
ENG-456 Added OAuth2 authentication support

This adds support for GitHub and Google OAuth providers.
Users can now sign in using their existing accounts.
```

With manual bump:

```sh
OPS-789 Changed database connection pooling

[bump:major]
```

## Pre-commit Hook

Validate commit messages using pre-commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/commitizen-tools/commitizen
    rev: v3.0.0
    hooks:
      - id: commitizen
        stages: [commit-msg]
```

## GitHub Actions Integration

Example workflow for automated releases:

```yaml
name: Release

on:
  push:
    branches: [main]

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          pip install commitizen cz-linear

      - name: Check for release
        id: check_release
        run: |
          echo "current_version=$(cz version -p)" >> $GITHUB_OUTPUT

      - name: Bump version
        run: |
          git config user.email "bot@example.com"
          git config user.name "Release Bot"
          cz bump --changelog --yes

      - name: Push changes
        run: |
          git push
          git push --tags
```

## Contributing

We welcome contributions! Here's how to get started:

### Development Setup

```bash
git clone https://github.com/quantivly/cz-linear.git
cd cz-linear
pip install -e ".[dev]"
```

### Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=cz_linear

# Run specific test file
pytest tests/test_validators.py
```

### Code Quality

```bash
# Format code
black cz_linear tests

# Lint
ruff check cz_linear tests

# Type check
mypy cz_linear
```

### Making Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b user/linear-123-my-feature`
3. Make your changes following the code style
4. Run tests and quality checks
5. Commit using the cz-linear format: `cz commit`
6. Push and create a pull request

### Adding New Verbs

To add a new verb:

1. Add it to `VERB_MAP` in `cz_linear/constants.py`
2. Choose the appropriate increment type
3. Add tests for the new verb
4. Update this README

## Project Structure

```sh
cz_linear/
├── __init__.py         # Package initialization
├── cz_linear.py        # Main plugin class
├── constants.py        # Verb mappings and constants
├── validators.py       # Input validation functions
├── parser.py          # Commit message parsing
├── exceptions.py      # Custom exceptions
└── config.py          # Configuration handling
```

## License

MIT License - see [LICENSE](LICENSE) file for details.
