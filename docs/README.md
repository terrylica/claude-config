# Claude Code Global Configuration Template

This repository serves as a template for Claude Code workspace configuration, providing standardized tools, automation, and team setup procedures.

## 🚀 Quick Navigation

| Category | Description | Key Documents |
| --- | --- | --- |
| 📋 **Standards** | Official Claude Code standards and references | [Session Storage Standard](standards/CLAUDE_SESSION_STORAGE_STANDARD.md) |
| 🏗️ **Architecture** | System design and architectural principles | [Architecture Overview](architecture/ARCHITECTURE.md) |
| ⚙️ **Setup** | Installation and configuration guides | [Team Setup](setup/TEAM_SETUP.md), [GPU Setup](setup/gpu-cloud-setup.md) |
| 🔄 **Sync** | Cross-platform synchronization workflows | [Sync Strategy](sync/claude-code-sync-strategy.md) |
| 🤖 **Agents** | AI agents and slash commands | [Agents](agents/AGENTS.md) |
| 📊 **Reports** | Analysis and project reports | [SAGE Sync Report](reports/MHR_SAGE_SYNC_REPORT.md) |

## Quick Start

**For team members - complete setup in 2 minutes:**

```bash
git clone <repo-url> ~/.claude
cd ~/.claude
./install-all-tools
```

## 📚 Documentation Structure

### 📋 Standards & References

Essential standards and official documentation for Claude Code compliance:

- [Claude Session Storage: Verified Standard](standards/CLAUDE_SESSION_STORAGE_STANDARD.md) - Docker-verified official session format
- [Official Files Reference](standards/CLAUDE_CODE_OFFICIAL_FILES.md) - Critical files that must not be moved/deleted

### 🏗️ Architecture

System design and architectural documentation:

- [Architecture Overview](architecture/ARCHITECTURE.md) - System architecture and design principles

### ⚙️ Setup & Configuration

Installation and configuration guides:

- [Team Setup Guide](setup/TEAM_SETUP.md) - Installation and usage guide
- [GPU Cloud Setup](setup/gpu-cloud-setup.md) - GPU workstation configuration

### 🔄 Synchronization

Cross-platform sync strategies and workflows:

- [Seamless Sync Setup](sync/seamless-sync-setup.md) - Sync configuration
- [Claude Code Sync Strategy](sync/claude-code-sync-strategy.md) - Synchronization strategies
- [Bidirectional Sync Demo](sync/bidirectional-sync-demo.md) - Sync demonstration
- [Sync Redesign Master Plan](sync/SYNC_REDESIGN_MASTER_PLAN.md) - Sync architecture

### 🤖 Agents

AI agent documentation:

- [Agent Configurations](agents/AGENTS.md) - Available AI agents and their capabilities

### 📊 Reports & Analysis

Project reports and analysis documentation:

- [MHR SAGE Sync Report](reports/MHR_SAGE_SYNC_REPORT.md) - Sync system analysis and recommendations

## Tools & Components

### SAGE Development Suite

- **Location**: `sage-aliases/`
- **Documentation**: [SAGE Tools Documentation](../sage-aliases/docs/README.md)
- **Commands**: `sage-dev`, `sage-sync`, `sage-status`, `gpu-ws`

### Documentation & Quality Tools

- **GFM Link Checker**: `gfm-link-checker/`
- **Documentation**: [GFM Checker Documentation](../gfm-link-checker/docs/README.md)
- **Command**: `gfm-check`

### Release Automation

- **git-cliff**: `tools/git-cliff/`
- **Documentation**: [git-cliff README](../tools/git-cliff/README.md)
- **Features**: Commitizen + git-cliff integration, language-agnostic version detection, 125K GitHub limit handling

### System & Productivity Tools

- **CNS Notification System**: `automation/cns/`

- **Documentation**: [CNS Documentation](../automation/cns/README.md)

- **Command**: `cns-notify`

### Agent Configurations

- **Location**: `agents/`
- **Documentation**: [Agent Configurations](agents/AGENTS.md)

## Architecture

This workspace follows hybrid architecture principles:

- **Source files**: Organized in structured directories
- **Executables**: Globally accessible via `~/.local/bin/`
- **Documentation**: Centralized in `docs/` directories
- **Universal access**: All tools work from any directory after installation

## Support

- **Installation Issues**: Re-run `./install-all-tools` for diagnostics
- **Tool Usage**: See individual tool documentation linked above
- **Team Setup**: Follow the [Team Setup Guide](setup/TEAM_SETUP.md)
