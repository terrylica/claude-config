# Claude Code User Memory

## Workspace-Wide Development Principles

### Language Evolution
- **Evolutionary Mindset**: Never use promotional language ("enhanced", "improved", "optimized") - everything is evolutionary by nature
- **Application Scope**: ALL Claude Code workspace content, documentation, commit messages, communications, and development work
- **Rationale**: Eliminates maintenance burden of constantly updating promotional qualifiers in evolving development environments

### Planning Philosophy
- **Logical Dependencies**: Never use time-based planning (hours, days, weeks) or roadmapping; organize by logical dependencies, priorities, and capabilities instead
- **Dynamic Evolution**: Objectives and implementations are dynamically evolutionary by nature

## Claude Code User Memory Documentation Principles

### Document Definition
- **Scope**: These principles apply _ONLY_ to this Claude Code user memory file Located in `.claude/CLAUDE.md`
- **Purpose**: This document serves as a high-level pointer/reference only
- **Rationale**: Detailed specifications belong in the actual script files to avoid redundancy

### Content Standards
- **Include**: Environment preferences, tool choices, file locations
- **Exclude**: Implementation details, parameters, version numbers, limitations, processing flows

## System Architecture & Environment

### Platform & Path Conventions
- **Target Platform**: Unix-like systems (macOS, Linux) - **Not designed for Windows compatibility**
- **Path Standards**: `$HOME` (resolves to `/Users/$USER` on macOS, `/home/$USER` on Linux)
- **Workspace Location**: `$HOME/.claude/` (follows dotfile convention)
- **Shell Environment**: POSIX-compliant shells (zsh, bash)
- **Portability**: All documentation MUST use Unix conventions (`$HOME`, `$USER`) for cross-user compatibility

### Universal Tool Access & Working Directory Preservation
- **Hybrid Architecture Strategy**: `$HOME/.local/bin/` for executables, `$HOME/.claude/tools/` for supporting files/configs
- **PATH Configuration**: Shell configuration includes ONLY `$HOME/.local/bin` in PATH (industry standard)
- **Clean Separation**: Executables globally accessible, source code and configs organized in .claude structure
- **Cross-Platform Consistency**: Same tool access pattern on macOS and Linux environments
- **Absolute Path Resolution**: Scripts use absolute paths to find supporting files in .claude structure
- **Architecture Pattern**: Tools use `uv run --directory` for self-contained environments while preserving working directory context
- **Working Directory Principle**: All workspace scripts MUST preserve user's current working directory - avoid `cd` operations that permanently change user context (subshell path resolution and save/restore patterns are acceptable)

### Current User Context
- Engineering lead responsible for features engineering for downstream seq-2-seq model consumption
- Advocate for SOTA tooling in Claude Code Max environment

## Development Environment & Tools

### Primary Toolchain
- **Python Management**: `uv` for all Python operations (`uv run`, `uv add`) - **Avoid**: pip, conda, pipenv
- **Python Version**: 3.10+, type checking disabled (development environment)
- **Libraries**: Prefer `httpx` over `requests`, `platformdirs` for cache directories
- **Remote Access**: Prefer `curl` over fetch
- **File Operations**: Prefer `Read`, `LS`, `Glob`, `Grep` over MCP filesystem tools (broader access)
- **Code Analysis**: `Semgrep`, `ast-grep`, `ShellCheck`

### Git Repository Detection
- `uv run python -c "import pathlib;g=next((x for x in [pathlib.Path.cwd()]+list(pathlib.Path.cwd().parents) if (x/'.git').exists()),pathlib.Path.cwd());print(g)"`

## Documentation Standards

### Claude Code Markdown Restrictions & README Policies
- **Global `~/.claude/`**: Markdown files allowed (configuration template)
- **Project `.claude/`**: NO markdown files - Claude Code interprets them as slash commands causing invocation conflicts
- **Root README Delegation**: NEVER create root `README.md` - use `docs/README.md` as main documentation (GitHub auto-renders)
- **Related Docs**: Use alternative naming (OVERVIEW.md, INDEX.md, GUIDE.md) for non-global `.claude/` directory documentation

### Link Validation Standards
- **Pre-edit Verification**: Verify all directory links have README.md or point to existing files
- **GitHub Behavior**: Directory links without README.md show empty pages/404 on GitHub
- **Validation Scope**: Check directory references, file paths, anchor links, relative paths
- **Security Audit**: Validate shell commands, file paths, user input handling in documentation examples

## Native Pattern Conformity

### Pattern Adherence Requirements
- **User Global Patterns** (`~/.claude/CLAUDE.md`): Language evolution, Unix conventions, tool preferences, documentation standards
- **Project Patterns** (`CLAUDE.md`): PPO, FPPA, NTPA, CFUP, APCF, AFPOE compliance
- **Cross-Pattern Validation**: Ensure harmony between user global and project requirements
- **Systematic Validation**: Apply audit methodology to verify pattern conformity

## DSQ: Direction Steering Questions

- **Clear Discrepancies**: Ask user key direction steering questions (DSQ) to ensure plan stays focused and consolidated toward user's preferred path.

## Success Gates & Success Sluices Terminology

- **Success Gates**: Major implementation milestones that must be validated before proceeding
- **Success Sluices**: Granular validation checkpoints between Success Gates that must be cleared before advancing

## APCF: Audit-Proof Commit Format for SR&ED Evidence Generation

- **Usage**: Request "APCF" or "apcf" to trigger automated SR&ED-compliant commit message generation.
- **Full Documentation**: See `/apcf` command for complete specifications, templates, and usage guidelines.

## Claude Code User Custom Extensions

### CNS (Conversation Notification System)
**Purpose**: Audio notification with context engineering support (clipboard currently disabled)

#### Core Files (Simplified Architecture - CNS System)
- **Configuration**: `.claude/automation/cns/config/cns_config.json` (notification and volume settings, clipboard disabled)
- **Main Script**: `.claude/automation/cns/conversation_handler.sh` (206 lines, audio processing)
- **Entry Point**: `.claude/automation/cns/cns_hook_entry.sh` (hook system integration)
- **Notification Hook**: `.claude/automation/cns/cns_notification_hook.sh` (audio notification with configurable volume + folder name announcement)
- **Manual Utility**: `cns-notify` (available globally via ~/.local/bin)
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

#### Universal Access
- **Usage**: `gfm-check [options]` (available globally via ~/.local/bin)
- **Zero Configuration**: Works from any workspace without system modifications

#### Core Files
- **Main Script**: `.claude/tools/gfm-link-checker/gfm_link_checker.py`
- **Command Wrapper**: `.claude/tools/gfm-link-checker/bin/gfm-check`
- **Project Config**: `.claude/tools/gfm-link-checker/pyproject.toml`