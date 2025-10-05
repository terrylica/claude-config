# Claude Code Global Configuration

**Purpose**: Centralized Claude Code workspace configuration and automation infrastructure

## 📚 Documentation

**Complete documentation**: [`docs/README.md`](docs/README.md)

## Quick Start

```bash
# Team setup (2 minutes)
git clone <repo-url> ~/.claude
cd ~/.claude
./install-all-tools
```

## Structure

- **`docs/`** - Complete documentation hub
- **`tools/`** - Standalone utilities (GFM checker, git-cliff, SAGE tools)
- **`automation/`** - CNS notification system, hooks
- **`commands/`** - Slash command extensions
- **`agents/`** - AI agent configurations
- **`specifications/`** - YAML specs for custom extensions

## Key Components

| Tool | Command | Documentation |
|------|---------|---------------|
| CNS Notifications | `cns-notify` | [`automation/cns/README.md`](automation/cns/README.md) |
| GFM Link Checker | `gfm-check` | [`tools/gfm-link-checker/docs/README.md`](tools/gfm-link-checker/docs/README.md) |
| git-cliff Release | (see docs) | [`tools/git-cliff/README.md`](tools/git-cliff/README.md) |
| SAGE Tools | `sage-dev` | [`tools/sage-aliases/docs/README.md`](tools/sage-aliases/docs/README.md) |
| Tmux Sessions | `tmux-session` | [`tmux/docs/README.md`](tmux/docs/README.md) |

## Global Instructions

**User memory**: [`CLAUDE.md`](CLAUDE.md) - Global instructions for all Claude Code sessions
