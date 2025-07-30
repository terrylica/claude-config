# Claude Code User Memory

## Claude Code User Memory Documentation Principles

### Document Definition
- **Scope**: These principles apply _ONLY_ to this Claude Code user memory file Located in `.claude/CLAUDE.md`
- **Purpose**: This document serves as a high-level pointer/reference only
- **Rationale**: Detailed specifications belong in the actual script files to avoid redundancy

### Content Standards
- **Include**: Environment preferences, tool choices, file locations
- **Exclude**: Implementation details, parameters, version numbers, limitations, processing flows
- **Planning Approach**: Never use time-based planning (hours, days, weeks) or roadmapping; organize by logical dependencies, priorities, and capabilities instead
- **Language Evolution**: Never use promotional language ("enhanced", "improved", "optimized") - everything is evolutionary by nature

### Technical Requirements
- **Portability**: All workspace documentation MUST use Unix conventions (`$HOME`, `$USER`) instead of explicit paths for cross-user compatibility
- **Platform Assumption**: Documentation assumes Unix-like systems; Windows compatibility is explicitly not supported

## Tool Usage Preferences
- **Remote Viewing**: Prefer `curl` over fetch
- **File Operations**: Prefer `Read`, `LS`, `Glob`, `Grep` over MCP filesystem tools (broader access)
- **Code Analysis**: `Semgrep`, `ast-grep`, `ShellCheck`

## System Architecture and Assumptions

**Target Platform**: Unix-like systems (macOS, Linux) - **Not designed for Windows compatibility**

**Standard Unix Conventions**:
- User home directory: `$HOME` (resolves to `/Users/$USER` on macOS, `/home/$USER` on Linux)
- Workspace location: `$HOME/.claude/` (follows dotfile convention)
- Shell environment: POSIX-compliant shells (zsh, bash)

**Current User Context**: 
- Engineering lead responsible for features engineering for downstream seq-2-seq model consumption
- Advocate for SOTA tooling in Claude Code Max environment
- The full system path to user directory: `$HOME` (resolves to `/Users/$USER` on macOS, `/home/$USER` on Linux) 

## DSQ: Direction Steering Questions

- **Clear Discrepancies**: Ask user key direction steering questions (DSQ) to ensure plan stays focused and consolidated toward user's preferred path.

## APCF: Audit-Proof Commit Format for SR&ED Evidence Generation

- **Usage**: Request "APCF" or "apcf" to trigger automated SR&ED-compliant commit message generation.
- **Full Documentation**: See `/apcf` command for complete specifications, templates, and usage guidelines.

## 🧠 Workspace

### DRA: Documentation & README Audit

- **Workspace README**: Use `docs/README.md` over root - GitHub auto-fallback renders it anyway
- **Python Commands**: Always use `uv` prefix (e.g., `uv run`, `uv add`) - never assume pip/python
- **Link Validation**: Before editing README.md files, verify all directory links have README.md or point to existing files
- **GitHub Behavior**: Directory links without README.md show empty pages/404 on GitHub
- **Broken Link Types**: Check directory references, file paths, anchor links, relative paths
- **Security Audit**: Validate shell commands, file paths, user input handling in documentation examples
- **Root README Policy**: Aggregate links only; delegate content to target files/directories
- **Related Docs**: GitHub Flavored Markdown Inter-linking (e.g. bi-directional navigation between master plan and research topics)

## Development Environment Preferences

- `uv run python -c "import pathlib;g=next((x for x in [pathlib.Path.cwd()]+list(pathlib.Path.cwd().parents) if (x/'.git').exists()),pathlib.Path.cwd());print(g)"`

### Python Package Management
- **Primary Tool**: `uv` for all Python operations
- **Commands**: Use `uv run` for operations
- **Tools**: uv, ruff (other tools available via uv install)  
- **Python**: 3.10+, type checking disabled (development environment)  
- **Avoid**: pip, conda, pipenv

### Python Library Preference

- Prefer `httpx` over `requests` 
- Uses `platformdirs` for platform-appropriate cache directories (not workspace dirs)

## Claude Code User Custom Extensions

### CNS (Conversation Notification System)
**Purpose**: Clipboard conversation tracking and audio notification with context engineering support

#### Core Files (Simplified Architecture - CNS System)
- **Configuration**: `.claude/automation/cns/config/cns_config.json` (clipboard, notification, and volume settings)
- **Main Script**: `.claude/automation/cns/conversation_handler.sh` (188 lines, clipboard processing)
- **Entry Point**: `.claude/automation/cns/cns_hook_entry.sh` (hook system integration)
- **Notification Hook**: `.claude/automation/cns/cns_notification_hook.sh` (Toy Story audio with configurable volume + folder name TTS)
- **Manual Utility**: `.claude/bin/cns-notify` (manual notification testing)
- **Debug Logs**: `/tmp/claude_cns_debug.log` (structured logging)

#### CRITICAL PRINCIPLE: Asynchronous Hook Architecture
**All CNS hooks MUST use fire-and-forget pattern to prevent session delays**

- **Pattern**: `{ actual_work } &` - spawn background and exit immediately
- **No Timeouts**: Remove timeout values from settings.json for true async hooks
- **Testing**: Hook execution must be < 10ms (script exit time, not work completion)
- **Anti-Pattern**: Never wait for clipboard processing, audio playback, or file operations
- **Enforcement**: Any hook causing session ending delays must be refactored to async pattern

### GitHub Flavored Markdown Link Checker
**Purpose**: Link integrity validation for local workspaces with GitHub-specific behavior

#### Core Files
- **Main Script**: `.claude/tools/gfm-link-checker/gfm_link_checker.py`
- **Command Wrapper**: `.claude/tools/gfm-link-checker/bin/gfm-check`
- **Setup Script**: `.claude/tools/gfm-link-checker/setup-gfm-checker.sh`
- **Project Config**: `.claude/tools/gfm-link-checker/pyproject.toml`