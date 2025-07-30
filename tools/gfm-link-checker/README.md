# GitHub Flavored Markdown Link Integrity Checker

Ultra-comprehensive link validation system for local workspaces with GitHub-specific behavior awareness.

## Features

- **GitHub-aware directory validation** - Checks for README.md auto-rendering
- **Precise anchor validation** - Implements GitHub's heading-to-anchor conversion rules  
- **Multi-format support** - Handles `.md`, `.markdown`, `.mdown`, `.mkdn` files
- **Git repository intelligence** - Workspace-aware relative path resolution
- **Comprehensive error reporting** - Line-precise validation with categorized errors
- **Configurable performance** - Optional external URL checking for speed
- **Dependency resilient** - Graceful fallback when requests unavailable

## Installation

```bash
# Run the setup script
./setup-gfm-checker.sh

# Or manually with uv
uv sync
```

## Usage

```bash
# Using local command wrapper
./bin/gfm-check

# Check specific workspace
./bin/gfm-check /path/to/workspace

# Skip external URLs (faster)
./bin/gfm-check --no-external

# Generate JSON report
./bin/gfm-check --format json --output report.json

# Direct uv execution
uv run gfm_link_checker.py
```

## Link Types Validated

- **Local files** - Relative and absolute path validation
- **Directories** - GitHub README.md auto-render checking  
- **Anchors** - Internal heading references with GFM rules
- **External URLs** - HTTP/HTTPS with intelligent fallbacks
- **Mailto links** - Basic email format validation

## GitHub Flavored Markdown Intelligence

This tool implements GitHub's exact behavior for:
- Directory link auto-rendering (checks for README.md)
- Heading anchor generation (lowercase, hyphens, special char removal)
- Relative path resolution from Git repository context
- Case-sensitive file system awareness

## Output Formats

- **Text** - Human-readable with error categorization
- **JSON** - Machine-readable for automation integration

Perfect for integration with pre-commit hooks, CI/CD pipelines, and local development workflows.