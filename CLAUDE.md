# Claude Code User Memory

- Apply neutral, promotional-free language to generated docs/comments and new identifiers only; never alter user text; use SemVer 2.0.0 (init 1.0.0 if stable else 0.1.0); bump MAJOR for breaking, MINOR for additive, PATCH for fixes; update versions consistently across README/docstrings/metadata.

## Planning

- **Machine-Readable**: Define and maintain OpenAPI 3.1.1 spec for persistent planning files
- **Logical Dependencies**: Organize by capabilities, not time-based roadmapping - use Success Gates/Sluices for validation checkpoints
- **Dynamic Evolution**: Objectives and implementations evolve dynamically

## System Architecture & Environment

### Platform & Path Conventions
- **Target Platform**: Unix-like systems (macOS, Linux) - not Windows compatible
- **Standards**: `$HOME/.claude/` workspace, POSIX shells, use Unix conventions (`$HOME`, `$USER`) for portability

### Universal Tool Access & Working Directory Preservation
- **Hybrid Architecture**: `$HOME/.local/bin/` for executables, `$HOME/.claude/tools/` for configs - scripts use absolute paths and preserve working directory
- **PATH Standard**: Only `$HOME/.local/bin` in PATH, cross-platform consistency, avoid `cd` operations that change user context

### Current User Context
- Engineering lead responsible for features engineering for downstream seq-2-seq model consumption

## Development Environment & Tools

### Primary Toolchain
- **Python Stack**: `uv` (management), `uv run --active python -m` (execution), `maturin` (Rust integration), 3.12+ - **Avoid**: pip, conda, standalone execution
- **Rust Stack**: `cargo`, cross-platform compilation, `cargo nextest run`, `cargo deny check`, coexists with Python
- **Libraries**: Prefer `httpx`, `platformdirs`, `curl` over `requests`, `fetch` - **Tools**: `Read`, `LS`, `Glob`, `Grep` over MCP
- **Analysis**: `Semgrep`, `ast-grep`, `ShellCheck` - **GPU**: `tensorflow-metal`, `jax`, `torch`, `cupy`
- **Finance**: `backtesting.py` ONLY, `rangebar` crate - **Prohibited**: bt, vectorbt, mlfinlab, commercial libs
- **Documentation**: ALL examples must use `uv run --active python -m` format, never standalone execution


### Mandatory Rust Code Quality Enforcement (2025 Best Practices)
- **Zero Tolerance Policy**: All commits blocked unless passing `cargo fmt --check`, `cargo clippy -- -D warnings`, and `cargo test`
- **Enforcement**: Pre-commit hooks, VS Code auto-format, GitHub Actions validation
- **Setup**: `chmod +x .git/hooks/pre-commit && pre-commit install`

## Documentation Standards

### LLM-Optimized Documentation Architecture
- **Machine-Readable Priority**: OpenAPI 3.1.0 specs, JSON Schema, YAML specifications take precedence over human documentation
- **Integration Targets**: Cursor IDE, Claude Code CLI, AI coding assistants

### Claude Code Markdown Restrictions & README Policies
- **Markdown Files**: Global `~/.claude/` allowed, project `.claude/` prohibited (slash command conflicts)
- **README Policy**: Use `docs/README.md`, not root `README.md` - alternative naming for non-global docs

## Claude Code User Custom Extensions

### CNS (Conversation Notification System)
**Specification**: [`.claude/specifications/cns-conversation-notification-system.yaml`](.claude/specifications/cns-conversation-notification-system.yaml)

### GitHub Flavored Markdown Link Checker
**Specification**: [`.claude/specifications/gfm-link-checker.yaml`](.claude/specifications/gfm-link-checker.yaml)

### Pushover Integration
**Specification**: [`.claude/specifications/pushover-integration.yaml`](.claude/specifications/pushover-integration.yaml)

### PyPI Publishing Methods
**Specification**: [`.claude/specifications/pypi-publishing-methods.yaml`](.claude/specifications/pypi-publishing-methods.yaml)

## Credential Management & Security

**Credential Management**: Doppler CLI (`doppler run -- <command>`) for zero-config credential injection
**Specification**: [`.claude/specifications/doppler-integration.yaml`](.claude/specifications/doppler-integration.yaml)

