# Claude Code User Memory

## Claude Code User Memory Documentation Principles
- **Scope**: These principles apply _ONLY_ to this Claude Code user memory file Located in `.claude/CLAUDE.md`
- **Purpose**: This document serves as a high-level pointer/reference only
- **Include**: Environment preferences, tool choices, file locations
- **Exclude**: Implementation details, parameters, version numbers, limitations, processing flows
- **Rationale**: Detailed specifications belong in the actual script files to avoid redundancy

## Tool Usage Preferences
- **Remote Viewing**: Prefer `curl` over fetch
- **File Operations**: Prefer `Read`, `LS`, `Glob`, `Grep` over MCP filesystem tools (broader access)
- **Code Analysis**: `Semgrep`, `ast-grep`, `ShellCheck`

## User Profiling and Local Path (user-specific info)

- Terry Li, Director of Operations of Eon Labs Ltd., an advocate to discover the latest SOTA toolings for vide coding and context engineering in Anthropic Claude Code Max environment, is responsible for features engineering for downstream see-2-seq model's consumption.
- The full macOS system path to user directory: `/Users/terryli/` 

## APCF: Audit-Proof Commit Format for SR&ED Evidence Generation

**Usage**: Request "APCF" or "apcf" to trigger automated SR&ED-compliant commit message generation.

**Full Documentation**: See `/apcf` command for complete specifications, templates, and usage guidelines.

## 🧠 Workspace

- `uv run python -c "import pathlib;g=next((x for x in [pathlib.Path.cwd()]+list(pathlib.Path.cwd().parents) if (x/'.git').exists()),pathlib.Path.cwd());print(g)"`

- **Tools**: uv, black, ruff, mypy, pytest  
- **Python**: 3.11+, type hints required  
- **Commands**: Use `make` or `uv run` for operations

### Documentation & README Audit Requirements

- **Workspace README**: Use `docs/README.md` over root - GitHub auto-fallback renders it anyway
- **Python Commands**: Always use `uv` prefix (e.g., `uv run`, `uv add`) - never assume pip/python
- **Link Validation**: Before editing README.md files, verify all directory links have README.md or point to existing files
- **GitHub Behavior**: Directory links without README.md show empty pages/404 on GitHub
- **Broken Link Types**: Check directory references, file paths, anchor links, relative paths
- **Security Audit**: Validate shell commands, file paths, user input handling in documentation examples
- **Root README Policy**: Aggregate links only; delegate content to target files/directories

## Development Environment Preferences

### Python Package Management
- **Primary Tool**: `uv` for all Python operations
- **Avoid**: pip, conda, pipenv

### Cache System

- Uses `platformdirs` for platform-appropriate cache directories (not workspace dirs)

## Claude Code User Custom Extensions

### Intelligent Text-to-Speech Hook System
**Purpose**: Audio feedback for Claude Code responses

#### Core Files (Modular Architecture - Phase 1 Complete)
- **Configuration**: `.claude/automation/tts/config/` (JSON-based settings)
- **Foundation**: `.claude/automation/tts/lib/common/` (config, logging, error handling)
- **Entry Point**: `.claude/automation/tts/tts_hook_entry.sh` (updated for modular system)
- **Legacy Script**: `.claude/automation/tts/claude_response_speaker.sh` (monolithic, compatibility)
- **Debug Logs**: `/tmp/claude_tts_debug.log` (structured logging)

### GitHub Flavored Markdown Link Checker
**Purpose**: Link integrity validation for local workspaces with GitHub-specific behavior

#### Core Files
- **Main Script**: `.claude/tools/gfm-link-checker/gfm_link_checker.py`
- **Command Wrapper**: `.claude/tools/gfm-link-checker/bin/gfm-check`
- **Setup Script**: `.claude/tools/gfm-link-checker/setup-gfm-checker.sh`
- **Project Config**: `.claude/tools/gfm-link-checker/pyproject.toml`