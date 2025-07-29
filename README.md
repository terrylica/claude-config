# Claude Code Workspace Configuration

> **Organizational Repository**: https://github.com/Eon-Labs/claude-config

This workspace contains comprehensive Claude Code configuration for cross-platform development with CNS (Conversation Notification System), APCF methodology, and development tools integration.

## 📁 Quick Navigation

| Component | Purpose | Documentation |
|-----------|---------|---------------|
| **[Core Configuration](docs/README.md)** | System overview and setup guide | Main documentation |
| **[Architecture](docs/ARCHITECTURE.md)** | System design and integration details | Technical architecture |
| **[CNS System](automation/cns/README.md)** | Conversation notification and clipboard tracking | CNS documentation |
| **[Tmux Integration](tmux/README.md)** | Simple session management | Tmux documentation |
| **[APCF Commands](commands/apcf.md)** | Audit-proof commit formatting | APCF methodology |
| **[Migration Guide](docs/REPOSITORY_MIGRATION.md)** | Repository migration documentation | Migration details |

## 🚀 Quick Start

1. **Setup**: Run `tmux/bin/setup-simple-tmux` for tmux integration
2. **Configuration**: Review `settings.json` for Claude Code hook settings  
3. **CNS**: Configure audio and clipboard in `automation/cns/config/cns_config.json`
4. **Commands**: Use `/apcf` for audit-proof commit message generation

## 🎯 Key Features

- **Cross-Platform**: Works on macOS and Linux with automatic platform detection
- **CNS Integration**: Automatic clipboard tracking and audio notifications  
- **APCF Methodology**: SR&ED-compliant commit message generation
- **Simple Tmux**: Clean session management without complex plugins
- **Organizational**: Ready for team collaboration and co-worker sharing

For detailed setup and usage instructions, see [docs/README.md](docs/README.md).