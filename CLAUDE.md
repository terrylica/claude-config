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
- **Architecture Pattern**: Tools use `uv run --active python -m --directory` for self-contained environments while preserving working directory context
- **Working Directory Principle**: All workspace scripts MUST preserve user's current working directory - avoid `cd` operations that permanently change user context (subshell path resolution and save/restore patterns are acceptable)

### Current User Context
- Engineering lead responsible for features engineering for downstream seq-2-seq model consumption
- Advocate for SOTA tooling in Claude Code Max environment

### Additional AI Research Resources

#### GPT-5 Thinking Model Integration
- **Availability**: Cheap and almost unlimited usage for extensive research
- **Usage Philosophy**: Don't hesitate to invoke GPT-5 thinking model at any point when in doubt

#### Research Prompt Generation Guidelines
**When to Use**: Configuration errors, API compatibility issues, parameter optimization, implementation uncertainty
**How to Structure Research Prompts**:
- **Context Section**: Current technical environment, library versions, specific error messages, data constraints
- **Problem Definition**: Exact challenges faced, failed approaches, specific blockers
- **Research Objectives**: Numbered list of specific questions needing systematic investigation  
- **Technical Environment**: Hardware specs, software versions, data characteristics
- **Research Methodology**: Request systematic literature review, documentation analysis, community examples
- **Deliverable Format**: Working code examples, parameter recommendations, troubleshooting guides
- **Success Criteria**: Measurable outcomes that eliminate trial-and-error approaches

#### Quality Standards
- Always verify GPT-5 research with real data and sufficient data length before claiming completion
- Use extensive context in research prompts to get targeted, actionable solutions
- Request specific implementation examples rather than theoretical explanations
- Focus on systematic investigation over quick fixes

## Defensive Programming Standards

### Data Authenticity Requirements
- **Real Data Only**: Never use fake data, mock data, synthetic data, or placeholder data even for testing
- **Production Quality Sources**: Always seek authentic, production-quality data sources
- **Data Integrity**: Validate all inputs at system boundaries with explicit type checking
- **Authenticity Verification**: Validate data authenticity and integrity at every processing boundary

### Input Validation Requirements  
- **Boundary Conditions**: Check for null, empty, and edge case values before processing
- **Format Validation**: Ensure data conforms to expected formats before consumption
- **Range Validation**: Verify numeric values fall within acceptable bounds

### Exception-Only Failure Principles
- **No Fallover Mechanisms**: Never implement failover, failsafe, or fallback mechanisms for data or model operations
- **Immediate Exception**: Systems must fail immediately with rich debug context, never continue with corrupted state
- **No Silent Failures**: Every anomaly, inconsistency, or boundary violation must raise explicit exceptions
- **Explicit Exceptions**: Raise structured exceptions with rich context for debugging
- **Early Detection**: Identify problems as close to source as possible

## Development Environment & Tools

### Primary Toolchain
- **Python Management**: `uv` for all Python operations (`uv run --active python -m`, `uv add`) - **Avoid**: pip, conda, pipenv
- **Module-Only Execution**: Mandatory `-m` flag with on-demand compatibility resolution and consolidation over proliferation
- **Python Version**: 3.12+, type checking disabled (development environment)
- **Libraries**: Prefer `httpx` over `requests`, `platformdirs` for cache directories
- **Remote Access**: Prefer `curl` over fetch
- **File Operations**: Prefer `Read`, `LS`, `Glob`, `Grep` over MCP filesystem tools (broader access)
- **Code Analysis**: `Semgrep`, `ast-grep`, `ShellCheck`

### Git Repository Detection
- `uv run --active python -m pathlib -c "import pathlib;g=next((x for x in [pathlib.Path.cwd()]+list(pathlib.Path.cwd().parents) if (x/'.git').exists()),pathlib.Path.cwd());print(g)"`

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
- **Project Patterns** (`CLAUDE.md`): PPO, COE, FPPA, NTPA, APCF compliance
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

## EPMS: Editable Package Management System

### Core Principle
**Universal Workspace Integration**: All packages (repos/, experiments/, tools/) are uv workspace members enabling seamless cross-package imports without sys.path manipulation.

### Architecture Benefits
- **Zero sys.path Hacks**: Clean Python imports across all workspace components
- **Live Development**: Changes in any package instantly available to all dependents
- **Dependency Transparency**: All package relationships explicit in pyproject.toml files
- **Universal Tool Access**: Scripts work from any directory without path discovery logic

### Integration Patterns
- **Third-Party Repos**: `repos/` packages (tirex, data-source-manager, finplot, nautilus_trader)
- **Internal Experiments**: `experiments/` packages (tirex-context-stability, research projects)
- **Development Tools**: `.claude/tools/` packages with global CLI access via ~/.local/bin
- **Test Environments**: Isolated package testing with full workspace dependency access

### Secure Sudo Helper
**Purpose**: Automated privilege escalation with security controls for system diagnostics

#### Universal Access
- **Usage**: `sudo-helper <command>` (available globally via ~/.local/bin)
- **Security**: Whitelist-based command filtering with audit logging

#### Core Files
- **Main Script**: `$HOME/.local/bin/sudo-helper` (whitelisted command execution)
- **Audit Log**: `$HOME/.sudo-helper.log` (complete usage tracking)

#### Security Features
- **Command Whitelist**: Only pre-approved diagnostic commands execute automatically
- **Audit Trail**: All usage logged with timestamps for security review
- **Graceful Fallback**: Non-whitelisted commands require manual sudo authentication
- **No Persistent Access**: Works within standard sudo timeout windows only