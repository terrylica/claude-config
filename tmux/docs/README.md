# Claude Code tmux Integration

An intelligent, zero-config tmux session management system for Claude Code with perfect compatibility and workspace-aware persistence.

## 🎯 Vision

**Invisible persistence with perfect compatibility** - Enhance Claude Code with tmux persistence while preserving 100% of its functionality and maintaining zero cognitive overhead for basic usage.

## 🏗️ Architecture

```
~/.claude/tmux/
├── bin/                          # Executable scripts
│   ├── claude-router.sh         # Intelligent command router
│   ├── session-manager.sh       # Session management utilities
│   └── installer.sh             # Automated installer
├── config/                       # Configuration files
│   ├── shell-integration.sh     # Main shell integration
│   └── tmux.conf               # Optimized tmux configuration
├── data/                         # Session data and logs
│   ├── workspace-sessions/      # Per-workspace session metadata
│   └── session-history.log     # Global session activity log
└── docs/                         # Documentation
    ├── README.md               # This file
    └── USAGE-EXAMPLES.md       # Real-world usage patterns
```

## 🚀 Quick Start

### One-Command Installation
```bash
~/.claude/tmux/bin/installer.sh
```

### Manual Integration
```bash
# Add to your shell configuration
echo 'source ~/.claude/tmux/config/shell-integration.sh' >> ~/.zshrc
source ~/.zshrc
```

## 🎯 Core Features

### Zero-Config Workspace Persistence
- **Automatic sessions**: Just use `claude` normally, get persistence automatically
- **Format:** `claude-{type}-{workspace}-{hash}`
- **Example:** `claude-default-my-project-a1b2c3`
- **Smart naming**: Collision-proof with path hashing
- **Context aware**: Each workspace gets isolated sessions

### Intelligent Command Routing
- **Interactive modes**: Automatic tmux persistence
- **Non-interactive**: Direct execution (--print, --output-format)
- **Subcommands**: Direct execution (config, mcp, doctor)
- **Conflicts**: User-prompted resolution (--continue, --resume)
- **Perfect compatibility**: All 28+ Claude flags preserved

### Progressive Complexity
- **Beginners**: Zero configuration, just works
- **Intermediate**: Named sessions for multiple contexts
- **Advanced**: Full session management and configuration
- **Power users**: Complete control over all aspects

## 📋 Command Reference

### Main Commands
| Command | Description |
|---------|-------------|
| `claude [args...]` | **Smart router** - All Claude Code functionality with intelligent persistence |
| `claude-session <cmd>` | Explicit session management for advanced users |
| `claude-help` | Show complete help and usage examples |

### Session Management
| Command | Description |
|---------|-------------|
| `claude-session start <name>` | Create named session in workspace |
| `claude-session list [--all]` | List workspace sessions (or all) |
| `claude-session attach <name>` | Attach to specific session |
| `claude-session kill <name\|--all>` | Kill session(s) |
| `claude-session clean [days]` | Remove old sessions |
| `claude-session status` | System health and statistics |
| `claude-session config` | Workspace configuration |

### Utility Commands
| Command | Description |
|---------|-------------|
| `claude-sessions` | Quick alias for `claude-session list` |
| `claude-status` | Quick alias for `claude-session status` |
| `claude-workspace` | Show current workspace info |
| `claude-debug` | Troubleshooting and diagnostics |
| `claude-migrate` | Check for old configurations |

## 🔧 Configuration

### Custom tmux Configuration
The system includes an optimized tmux configuration at `~/.claude/tmux/config/tmux.conf` with:
- Enhanced visual indicators
- Mouse support
- Vi-style key bindings
- Custom status bar for Claude sessions

### Environment Variables
- `CLAUDE_TMUX_MANAGER`: Path to manager script (auto-set)

## 📊 Session Management

### Session Lifecycle
1. **Creation**: Auto-named based on workspace + timestamp
2. **Logging**: All sessions tracked in persistent history
3. **Selection**: Visual picker with context information
4. **Cleanup**: Automatic removal of old sessions

### Data Storage
- Session history: `~/.claude/tmux/data/session_history.log`
- Format: `timestamp | session_name | workspace_path`

## 🛠️ Advanced Usage

### Automated Cleanup
```bash
# Remove sessions older than 3 days
claude-cleanup 3

# Add to crontab for weekly cleanup
0 2 * * 0 ~/.claude/tmux/bin/tmux_claude_manager.sh cleanup 7
```

### Integration with Existing Workflows
- Compatible with existing tmux configurations
- Preserves user's tmux customizations
- Non-intrusive installation process

## 🔍 Troubleshooting

### Common Issues
- **Session not found**: Use `claude-list` to verify active sessions
- **Permission denied**: Ensure scripts are executable (`chmod +x`)
- **Alias not working**: Source the configuration (`source ~/.zshrc`)

### Debug Information
- Session logs: `~/.claude/tmux/data/session_history.log`
- Test installation: `~/.claude/tmux/bin/tmux_installer.sh`

## 🎨 Design Philosophy

### Modularity
- Clear separation of concerns
- Self-contained components
- Easy to maintain and extend

### User Experience
- Intuitive command naming
- Visual feedback and status indicators
- Graceful error handling

### Integration
- Respects existing tmux workflows
- Compatible with various shell configurations
- Non-destructive installation

## 📈 Benefits

### Development Workflow
- **Persistence**: Sessions survive terminal crashes and system restarts
- **Organization**: Clear workspace-based session naming
- **Efficiency**: Quick resume and smart selection
- **History**: Complete audit trail of development sessions

### System Design
- **Modular**: Clean directory organization
- **Extensible**: Easy to add new features
- **Maintainable**: Self-documenting code structure
- **Reliable**: Robust error handling and edge case management

---

*For detailed setup instructions, see [TMUX_SETUP.md](./TMUX_SETUP.md)*