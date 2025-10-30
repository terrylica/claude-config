# Background Workspace Synchronization

## Current Status: ✅ SETUP DETECTED

### ZeroTier Performance Analysis

- **Connection Type**: DIRECT (peer-to-peer, not relayed)
- **Latency**: 7ms (suitable for same LAN)
- **Local Network Detection**: ✅ Working (192.168.0.111)
- **Overhead**: Minimal - ZeroTier using local network directly

**Result**: ZeroTier is NOT slowing down connectivity - it's using local network speeds!

### Syncthing Installation Status

- **macOS**: ✅ Installed via Homebrew
- **GPU Workstation**: ✅ Installed in user space (~/bin/syncthing)

## Setup Phase 1: Initialize Syncthing (5 minutes)

### Start Syncthing on Both Machines

#### On macOS:

```bash
# Start Syncthing service
brew services start syncthing

# Get your Device ID
syncthing --device-id
```

#### On GPU Workstation:

```bash
# Start Syncthing (will auto-create config)
ssh zerotier-remote "~/bin/syncthing --no-browser --no-restart > ~/syncthing.log 2>&1 &"

# Get remote Device ID
ssh zerotier-remote "~/bin/syncthing --device-id"
```

### Web Interface Access

- **macOS**: http://localhost:8384
- **Remote**: http://172.25.253.142:8384 (via ZeroTier)

## Setup Phase 2: Configure Sync

### 1. Add Remote Device

1. Open http://localhost:8384 on your Mac
1. Click "Add Remote Device"
1. Enter GPU workstation's Device ID
1. Name it "GPU Workstation"
1. Save

### 2. Create Shared Folder

1. Click "Add Folder"
1. **Folder Path**: `/Users/terryli/eon/nt/`
1. **Folder ID**: `nt-workspace`
1. **Share with**: Select "GPU Workstation"
1. Additional Settings:
   - **Ignore Patterns**: Add these lines:
     ```
     .git/objects/**
     .git/logs/**
     **/.venv/
     **/node_modules/
     **/__pycache__/
     **/.pytest_cache/
     **/.ruff_cache/
     **/*.pyc
     **/trade_logs/*.csv
     ```
1. Save

### 3. Accept on Remote

1. SSH to remote: `ssh zerotier-remote`
1. Open remote web interface or accept via command line
1. Accept the shared folder to `~/eon/nt/`

## Setup Phase 3: Create Quick Commands

### Add to ~/.claude/gpu-workstation-aliases.sh:

```bash
# Syncthing status and control
alias sync-status='curl -s http://localhost:8384/rest/system/status | jq .myID'
alias sync-conflicts='curl -s http://localhost:8384/rest/db/status?folder=nt-workspace | jq .needFiles'
alias sync-pause='curl -X POST http://localhost:8384/rest/system/pause'
alias sync-resume='curl -X POST http://localhost:8384/rest/system/resume'

# Quick workspace switch
alias work-local='echo "Working locally - changes sync automatically"'
alias work-remote='echo "Switching to remote work..." && ssh zerotier-remote'

# Sync verification
alias sync-check='echo "=== Local Status ===" && ls -la ~/eon/nt/ | head -5 && echo "=== Remote Status ===" && ssh zerotier-remote "ls -la ~/eon/nt/" | head -5'
```

## Phase 4: Seamless Workflow

### Daily Usage Pattern:

#### Working Locally (macOS):

```bash
cd ~/eon/nt
# Edit files with Claude Code, VS Code, etc.
# Changes automatically sync in background to GPU workstation
```

#### Switching to Remote Work:

```bash
work-remote  # SSH to GPU workstation
cd ~/eon/nt  # Same workspace, kept in sync
# Work directly on GPU workstation for TiRex validation
# Changes automatically sync back to macOS
```

#### Sync Monitoring:

```bash
sync-status    # Check sync health
sync-conflicts # Check for any conflicts
sync-check     # Verify both sides are in sync
```

## Performance Characteristics

### Background Sync Performance:

- **File Detection**: Real-time (inotify/kqueue file watching)
- **Transfer Speed**: Full local network speed (via ZeroTier direct P2P)
- **CPU Usage**: Minimal background process
- **Conflict Resolution**: Automatic with versioning

### Network Usage:

- **Same LAN**: Direct local network transfer
- **External**: ZeroTier P2P connection (still direct after handshake)
- **Bandwidth**: Only changed files transfer (delta sync)

## Troubleshooting

### If Sync is Slow:

```bash
# Check if connection is still DIRECT
sudo zerotier-cli peers | grep 8f53f201b7

# Restart Syncthing if needed
brew services restart syncthing
ssh zerotier-remote "pkill syncthing && ~/bin/syncthing --no-browser --no-restart > ~/syncthing.log 2>&1 &"
```

### Conflict Resolution:

- Syncthing creates `.sync-conflict` files for manual review
- Original files are never overwritten
- Both versions preserved until manually resolved

### Exclude Large Files:

Add to ignore patterns:

```
**/data_cache/*.parquet
**/trade_logs/*.csv
**/.git/objects/**
```

## Selective Sync

### For Different Work Patterns:

- **Code Only**: Sync just `/src/` and `/docs/`
- **Full Workspace**: Sync everything except data files
- **Results Only**: Separate sync for GPU computation results

### Multiple Folder Setup:

1. **nt-code**: Source code only
1. **nt-data**: Data files (larger, less frequent sync)
1. **nt-results**: GPU computation results

## Security Notes

### ZeroTier Security:

- All traffic encrypted end-to-end
- Direct P2P connection (no relay servers for your setup)
- Network access controlled by ZeroTier network admin

### Syncthing Security:

- Device-to-device encryption
- No cloud servers involved
- Local network traffic only

## Quick Start Commands

```bash
# Start everything
brew services start syncthing
ssh zerotier-remote "~/bin/syncthing --no-browser --no-restart > ~/syncthing.log 2>&1 &"

# Check status
sync-status
sync-check

# Work seamlessly
work-local   # For local development
work-remote  # For GPU validation work
```

---

**Status**: Ready for seamless background synchronization\
**Performance**: Optimal (ZeroTier using direct local network)\
**Workflow**: Switch between machines instantly with automatic sync
