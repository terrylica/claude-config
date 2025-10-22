# Claude Code User Memory

**Architecture**: Link Farm + Hub-and-Spoke with Progressive Disclosure (essentials only, each doc links deeper, single source of truth per topic)

**Navigation Index**: [`docs/INDEX.md`](docs/INDEX.md) - Hub-and-spoke documentation architecture

**Quick Links**: [Tools](tools/) | [Specifications](specifications/) | [Agents](docs/agents/AGENTS.md) | [Commands](docs/commands/commands.md) | [Docs](docs/)

---

## Conventions

- Apply neutral, promotional-free language to generated docs/comments and new identifiers only; never alter user text
- Use SemVer 2.0.0 (init 1.0.0 if stable else 0.1.0); bump MAJOR for breaking, MINOR for additive, PATCH for fixes
- Update versions consistently across README/docstrings/metadata
- **File Paths**: ALWAYS output absolute paths starting with `/` with space after extension before punctuation (e.g., `/path/to/file.md ` not `path/to/file.md.`) - Ghostty Cmd+click requires this, no exceptions

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
**Python**: `uv` (management), `uv run --active python -m` (execution), 3.12+ - **Avoid**: pip, conda, setuptools, poetry
**Rust**: `cargo`, `cargo nextest run`, `cargo deny check`, pre-commit hooks mandatory
**Containers**: Colima + Docker CLI (Homebrew)
**Full Catalog**: [`docs/setup/toolchain.md`](docs/setup/toolchain.md) - Complete tool preferences and package standards

## Documentation Standards

### LLM-Optimized Documentation Architecture
- **Machine-Readable Priority**: OpenAPI 3.1.0 specs, JSON Schema, YAML specifications take precedence over human documentation
- **Integration Targets**: Cursor IDE, Claude Code CLI, AI coding assistants

### Claude Code Markdown Restrictions & README Policies
- **Markdown Files**: Global `~/.claude/` allowed, project `.claude/` prohibited (slash command conflicts)
- **README Policy**: Use `docs/README.md`, not root `README.md` - alternative naming for non-global docs

## Global Skills

**Location**: `~/.claude/skills/` - Hierarchical structure, skills activate automatically

**Available Skills**:
- **python/api-documentation** - Pydantic v2 API documentation patterns
- **credentials/doppler-workflows** - PyPI publishing and AWS credential management via Doppler
- **latex/setup** - MacTeX installation and environment configuration
- **latex/tables** - tabularray package for modern table creation
- **latex/build** - latexmk build automation and live preview
- **troubleshooting/session-recovery** - Claude Code session troubleshooting

**Note**: Skills load contextually when relevant. Focused, single-capability design with progressive disclosure.

## Terminal & Shell Configuration
**Terminals**: [Ghostty](docs/setup/terminal-setup.md) (emoji tabs, session restore) | [Kitty](docs/setup/terminal-setup.md) (splits)
**Editor**: Helix (`hx`) - Modal editor with LSP, tree-sitter
**Multiplexer**: [Zellij](docs/setup/README.md) - Crash recovery, balanced power-user setup (50K scrollback, 10K recovery)
**Shell**: [Atuin](specifications/atuin-shell-history.yaml) (history sync) | [ccstatusline](https://github.com/sirmalloc/ccstatusline) (status bar) | [OSC52](docs/setup/ssh-clipboard-osc52.md) (SSH clipboard)
