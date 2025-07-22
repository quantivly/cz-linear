# cz-linear

A [Commitizen](https://commitizen-tools.github.io/commitizen/) plugin that implements Linear issue tracking conventions for commit messages.

## Overview

This plugin enforces the Linear commit message format:
```
<ISSUE-ID> <Past-tense-verb> <description>
```

Example:
```
ENG-1234 Fixed authentication bug in login flow
```

## Features

- **Automatic version bumping** based on commit verbs (major/minor/patch)
- **Interactive commit creation** with `cz commit`
- **Linear issue ID validation** (e.g., ENG-123, BUG-456)
- **Manual bump overrides** using `[bump:TYPE]` in commit messages
- **Changelog generation** with Linear issue references
- **Pre-commit hook support** for commit message validation

## Installation

### Requirements

- Python 3.8 or higher
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

```
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
- And many more...

See the full list in the [source code](cz_linear/cz_linear.py).

## Commit Message Format

### Structure
```
<ISSUE-ID> <Verb> <description>

[optional body]

[bump:major|minor|patch] (optional)
```

### Rules
- **Issue ID**: 2+ uppercase letters, dash, number (e.g., `ENG-123`, `PROJ-4567`)
- **Verb**: Past-tense verb from the approved list
- **Description**: Brief summary of the change
- **Body**: Optional detailed explanation
- **Manual bump**: Optional override for version detection

### Examples

```
BUG-123 Fixed null pointer exception in user service
```

```
ENG-456 Added OAuth2 authentication support

This adds support for GitHub and Google OAuth providers.
Users can now sign in using their existing accounts.
```

```
OPS-789 Changed database connection pooling

[bump:major]
```

## Pre-commit Hook

Validate commit messages using pre-commit:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/commitizen-tools/commitizen
    rev: v3.0.0  # replace with latest version
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
          python-version: '3.11'
          
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

## Development

### Setup Development Environment

```bash
git clone https://github.com/yourusername/cz-linear.git
cd cz-linear
pip install -e ".[dev]"
```

### Run Tests

```bash
pytest
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

### Building for Distribution

```bash
# Install build tools
pip install build

# Build the package
python -m build
```

## License

MIT License - see [LICENSE](LICENSE) file for details.
