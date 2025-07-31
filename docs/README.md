# Claude Code Global Configuration Template

This repository serves as a comprehensive template for Claude Code workspace configuration, providing standardized tools, automation, and team setup procedures.

## Quick Start

**For team members - complete setup in 2 minutes:**
```bash
git clone <repo-url> ~/.claude
cd ~/.claude
./install-all-tools
```

## Documentation

- **[Team Setup Guide](TEAM_SETUP.md)** - Complete installation and usage guide
- **[Architecture Overview](ARCHITECTURE.md)** - System architecture and design principles
- **[Seamless Sync Setup](seamless-sync-setup.md)** - Advanced sync configuration
- **[Claude Code Sync Strategy](claude-code-sync-strategy.md)** - Synchronization strategies
- **[Bidirectional Sync Demo](bidirectional-sync-demo.md)** - Sync demonstration
- **[GPU Cloud Setup](gpu-cloud-setup.md)** - GPU workstation configuration
- **[Official Files Reference](CLAUDE_CODE_OFFICIAL_FILES.md)** - Claude Code file specifications

## Tools & Components

### SAGE Development Suite
- **Location**: `tools/sage-aliases/`
- **Documentation**: [SAGE Tools Documentation](../tools/sage-aliases/docs/README.md)
- **Commands**: `sage-dev`, `sage-sync`, `sage-status`, `gpu-ws`

### Documentation & Quality Tools
- **GFM Link Checker**: `tools/gfm-link-checker/`
- **Documentation**: [GFM Checker Documentation](../tools/gfm-link-checker/docs/README.md)
- **Command**: `gfm-check`

### System & Productivity Tools
- **CNS Notification System**: `automation/cns/`
- **Documentation**: [CNS Documentation](../automation/cns/README.md)
- **Command**: `cns-notify`

- **Tmux Session Management**: `tmux/`
- **Documentation**: [Tmux Tools Documentation](../tmux/docs/README.md)
- **Commands**: `tmux-session`, `tmux-list`, `tmux-kill`

### Command Extensions
- **Location**: `commands/`
- **Documentation**: [Command Extensions Documentation](command-extensions.md)

### Agent Configurations
- **Location**: `agents/`
- **Documentation**: [Agent Configurations Documentation](../agents/docs/)

## Architecture

This workspace follows hybrid architecture principles:
- **Source files**: Organized in structured directories
- **Executables**: Globally accessible via `~/.local/bin/`
- **Documentation**: Centralized in `docs/` directories
- **Universal access**: All tools work from any directory after installation

## Support

- **Installation Issues**: Re-run `./install-all-tools` for diagnostics
- **Tool Usage**: See individual tool documentation linked above
- **Team Setup**: Follow the [Team Setup Guide](TEAM_SETUP.md)