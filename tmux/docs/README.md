# Simple Tmux Session Manager

**Purpose**: Clean, minimal tmux session management with smart naming

## Overview
Simple tmux session management without plugins, persistence, or complexity. Just smart folder-based naming and clean commands.

## Quick Start
```bash
# Load shell integration
exec zsh

# Basic usage
ts              # Create/attach session using folder name
tl              # List sessions
tk <name>       # Kill session
```

## Features
- 🎯 **Smart naming**: Folder-based session names with dot-folder awareness
- 🚀 **Simple commands**: `ts`, `tl`, `tk` aliases
- 🧹 **Clean**: No plugins, no persistence, no background processes
- ⚡ **Fast**: Pure tmux commands under the hood
- 📋 **Transparent**: You can see exactly what's happening

## Contents
```
bin/
├── setup-simple-tmux     # Initial setup script
├── tmux-session          # Main session manager
├── tmux-list            # Session listing
└── tmux-kill           # Session termination

config/
├── tmux.conf           # Clean tmux configuration
└── simple-shell-integration.sh  # Shell aliases

SIMPLE-USAGE.md         # Detailed documentation
```

## Core Philosophy
**Simple tools for simple needs.** Tmux does session management perfectly - no plugins required.

For detailed usage, see [SIMPLE-USAGE.md](./SIMPLE-USAGE.md)