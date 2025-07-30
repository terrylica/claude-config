# Claude Code Global Configuration Template

> **Organizational Repository**: https://github.com/Eon-Labs/claude-config

**Personal preferences for all projects** - A comprehensive Claude Code configuration template that provides consistent workflows, automation, and tooling across every project you work on.

## What This Provides

This repository serves as your **global `~/.claude/` directory template**, containing:
- **Cross-project consistency** - Same tools and workflows everywhere
- **Automated notifications** - Never miss Claude responses  
- **Professional commit formatting** - SR&ED-compliant APCF methodology
- **Intelligent workspace integration** - Seamless tmux, automation, and tooling
- **Team-shareable configuration** - Standardize workflows across your organization

**Installation**: Copy this entire directory structure to `~/.claude/` for instant global Claude Code configuration.

## 🤔 Is This For You?

**Yes, if you want to:**
- Get audio notifications when Claude finishes responses
- Generate professional commit messages automatically  
- Share configurations with teammates
- Work more efficiently with Claude Code

**Details**: [System overview and requirements →](docs/README.md)

## 📁 Quick Navigation

| Component | Purpose | Documentation |
|-----------|---------|---------------|
| **[Core Configuration](docs/README.md)** | System overview and setup guide | Main documentation |
| **[Architecture](docs/ARCHITECTURE.md)** | System design and integration details | Technical architecture |
| **[User Memory & Preferences](CLAUDE.md)** | Global user instructions and APCF methodology | User configuration |
| **[System Files Documentation](CLAUDE_CODE_OFFICIAL_FILES.md)** | Critical files safety reference | System file guide |
| **[CNS System](automation/cns/README.md)** | Conversation notification and clipboard tracking | CNS documentation |
| **[Tmux Integration](tmux/README.md)** | Simple session management | Tmux documentation |
| **[APCF Commands](commands/apcf.md)** | Audit-proof commit formatting | APCF methodology |
| **[Migration Guide](docs/REPOSITORY_MIGRATION.md)** | Repository migration documentation | Migration details |

## 🚀 Quick Start

**New to Claude Code?** [Install guide →](https://docs.anthropic.com/claude/docs/claude-code)

**Ready to configure your setup:**
1. **Copy this workspace** to your `~/.claude/` directory
2. **Run setup**: `tmux/bin/setup-simple-tmux` 
3. **Try it**: Type `/apcf` in Claude Code to generate commit messages

**Detailed setup**: [Complete installation guide →](docs/README.md)

## 🎯 What You Get

- **Never miss Claude responses** with audio notifications → [CNS docs](automation/cns/README.md)
- **Professional commit messages** generated automatically → [APCF guide](commands/apcf.md)  
- **Clean tmux sessions** without configuration hassle → [Tmux setup](tmux/README.md)
- **Team-ready** configurations for sharing → [Architecture details](docs/ARCHITECTURE.md)
- **Cross-platform** support (macOS, Linux) → [Platform requirements](docs/README.md#system-requirements)

**Full documentation**: [Complete guide →](docs/README.md)