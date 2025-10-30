# Atuin Shell History Sync

**Purpose**: Encrypted cloud-synced shell history with SQLite backend and fuzzy search

**Specification**: [`specifications/atuin-shell-history.yaml`](../../specifications/atuin-shell-history.yaml)

## Features

- 🔐 **End-to-end encryption** - History encrypted on-device before cloud sync
- ☁️ **Cloud backup** - Automatic sync to Atuin's official server
- 🔍 **Fuzzy search** - Enhanced Ctrl+R with context-aware search
- 💾 **SQLite backend** - Fast local database (~10MB for extensive history)
- 🔄 **Multi-machine sync** - Same history across all devices
- 🔑 **Mnemonic encryption key** - 24-word phrase for key recovery

## Installation

```bash
# Install via Homebrew
brew install atuin

# Add to shell (zsh)
echo 'eval "$(atuin init zsh)"' >> ~/.zshrc

# Reload shell
source ~/.zshrc

# Import existing history
atuin import auto
```

## Configuration

**Location**: `~/.config/atuin/config.toml`

**Key settings**:

```toml
# Enable automatic sync
auto_sync = true

# Sync every 5 minutes when running commands
sync_frequency = "5m"

# Official Atuin sync server
sync_address = "https://api.atuin.sh"
```

## Cloud Sync Setup

### Registration (First Time)

```bash
atuin register -u <username> -e <email>
# Enter password when prompted
# Your encryption key is automatically generated
```

### Backup Encryption Key

```bash
atuin key
```

**⚠️ CRITICAL**: Save this 24-word mnemonic phrase securely. Store in:

- Password manager (1Password, Bitwarden, etc.)
- Doppler (recommended): `doppler secrets set ATUIN_KEY="<24-word-phrase>" --project claude-config --config dev`

### Login (Other Machines)

```bash
atuin login -u <username>
# Enter password
# Enter encryption key when prompted
```

## Credential Storage (Doppler)

**Project**: `claude-config/dev`

**Stored secrets**:

```bash
# Username
doppler secrets set ATUIN_USERNAME="<username>" --project claude-config --config dev

# Email
doppler secrets set ATUIN_EMAIL="<email>" --project claude-config --config dev

# Encryption key (24-word mnemonic)
doppler secrets set ATUIN_KEY="<24-word-phrase>" --project claude-config --config dev

# Password (optional, for automated setup)
doppler secrets set ATUIN_PASSWORD="<password>" --project claude-config --config dev
```

**Retrieve credentials**:

```bash
doppler secrets get ATUIN_USERNAME ATUIN_EMAIL ATUIN_KEY --project claude-config --config dev --plain
```

## Usage

### Interactive Search (Enhanced Ctrl+R)

```bash
# Press Ctrl+R to open Atuin search interface
# Type to fuzzy search across all history
# Arrow keys to navigate, Enter to execute, Tab to edit
```

### Command-line Search

```bash
# Search history
atuin search <query>

# Search with filters
atuin search --cwd <directory>  # Filter by directory
atuin search --exit 0           # Only successful commands
```

### Sync Operations

```bash
# Check sync status
atuin status

# Force immediate sync
atuin sync

# View statistics (requires interactive shell)
atuin stats
```

## Multi-Machine Setup

### Quick Setup with Doppler

```bash
# Install Atuin
brew install atuin

# Add to shell
echo 'eval "$(atuin init zsh)"' >> ~/.zshrc
source ~/.zshrc

# Login using Doppler credentials (if password is stored)
doppler run --project claude-config --config dev -- sh -c '
  echo "$ATUIN_PASSWORD" | atuin login -u "$ATUIN_USERNAME" -e "$ATUIN_EMAIL" -k "$ATUIN_KEY"
'

# Manual login (if password not stored)
atuin login -u $(doppler secrets get ATUIN_USERNAME --project claude-config --config dev --plain)
# Enter password and encryption key when prompted
```

## File Locations

- **Database**: `~/.local/share/atuin/history.db` (SQLite)
- **Encryption key**: `~/.local/share/atuin/key`
- **Session token**: `~/.local/share/atuin/session`
- **Config**: `~/.config/atuin/config.toml`

## Security Model

1. **Encryption key generation**: Created locally during registration
1. **Key storage**: Stored in `~/.local/share/atuin/key` (never leaves device)
1. **Password**: Used only for authentication (not encryption)
1. **Data encryption**: All history encrypted with local key before upload
1. **Server blindness**: Atuin servers cannot decrypt your history

## Troubleshooting

### Sync not working

```bash
# Check status
atuin status

# Verify configuration
cat ~/.config/atuin/config.toml | grep -E "(auto_sync|sync_address|sync_frequency)"

# Force sync
atuin sync
```

### Lost encryption key

If you lose your encryption key:

- Check Doppler: `doppler secrets get ATUIN_KEY --project claude-config --config dev --plain`
- Check local file: `cat ~/.local/share/atuin/key`
- If both lost: History is unrecoverable (end-to-end encryption)

## Version

- **Atuin**: 18.8.0
- **Protocol**: Sync v2 (records-based)
- **Database**: SQLite 3.46.0
