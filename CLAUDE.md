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

### Python Library Preference

- Prefer `httpx` over `requests` 
- Uses `platformdirs` for platform-appropriate cache directories (not workspace dirs)

## Claude Code User Custom Extensions

### CNS (Conversation Notification System)
**Purpose**: Clipboard conversation tracking and audio completion notification for Claude Code responses

#### Core Files (Simplified Architecture - CNS System)
- **Configuration**: `.claude/automation/cns/config/cns_config.json` (clipboard and sound settings)
- **Main Script**: `.claude/automation/cns/conversation_handler.sh` (168 lines, clipboard + glass sound only)
- **Entry Point**: `.claude/automation/cns/cns_hook_entry.sh` (hook system integration)
- **Glass Sound**: `.claude/automation/cns/glass_sound_wrapper.sh` (separate audio notification)
- **Debug Logs**: `/tmp/claude_cns_debug.log` (structured logging)

#### CRITICAL PRINCIPLE: Asynchronous Hook Architecture
**All CNS hooks MUST use fire-and-forget pattern to prevent session delays**

- **Pattern**: `{ actual_work } &` - spawn background and exit immediately
- **No Timeouts**: Remove timeout values from settings.json for true async hooks
- **Testing**: Hook execution must be < 10ms (script exit time, not work completion)
- **Anti-Pattern**: Never wait for clipboard processing, sound playback, or file operations
- **Enforcement**: Any hook causing session ending delays must be refactored to async pattern

### GitHub Flavored Markdown Link Checker
**Purpose**: Link integrity validation for local workspaces with GitHub-specific behavior

#### Core Files
- **Main Script**: `.claude/tools/gfm-link-checker/gfm_link_checker.py`
- **Command Wrapper**: `.claude/tools/gfm-link-checker/bin/gfm-check`
- **Setup Script**: `.claude/tools/gfm-link-checker/setup-gfm-checker.sh`
- **Project Config**: `.claude/tools/gfm-link-checker/pyproject.toml`