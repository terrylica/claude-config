# CNS (Conversation Notification System)

Audio and Pushover notifications for Claude Code responses with session metadata (clipboard disabled).

## Architecture Overview

CNS provides dual-output notifications when Claude Code completes responses: local audio (afplay + say) and remote Pushover notifications with rich context metadata.

### Current System (CNS v2.0.0)
- **Main Script**: `conversation_handler.sh` (262 lines) - Audio + Pushover notification processing
- **Configuration**: `config/cns_config.json` - System settings + Pushover credentials (git-based)
- **Entry Point**: `cns_hook_entry.sh` - Routes local/remote environments
- **Local Audio**: `cns_notification_hook.sh` - Audio playback with folder name text-to-speech
- **Remote Client**: `tools/cns-remote-client.sh` - SSH remote notification client

## Functionality

### ✅ Active Features
- **Dual Notifications**: Local audio (macOS) + Pushover (cross-platform)
- **Session Metadata**: username@hostname, folder, session ID, hook event
- **Git-based Credentials**: Pushover credentials in cns_config.json (team-shared, zero-setup deployment)
- **Text-to-Speech**: Folder name announcement with tmux context detection
- **Volume Control**: Configurable notification volume (local audio only)
- **Async Processing**: Fire-and-forget background processing (<10ms hook execution)
- **Cross-platform**: macOS (audio + Pushover), Linux (Pushover only)

### 📱 Pushover Notification Format
```
Title: CNS: terryli@Terrys-MacBook-Pro
Message:
  📁 ml-feature-set
  ✅ Analysis complete (first 200 chars of response)

  🆔 b31bc615 | Stop
```

### ❌ Currently Disabled Features
- **Clipboard Tracking**: Disabled (`clipboard_enabled: false` in config)

## Configuration

**File**: `config/cns_config.json`

```json
{
  "note": "CNS (Conversation Notification System) - audio and Pushover notifications",
  "features": {
    "enable_clipboard_debug": true,
    "enable_cns_notification": true
  },
  "audio": {
    "notification_volume": 0.3,
    "volume_note": "Volume level for notification audio (0.0 = silent, 1.0 = full volume)"
  },
  "pushover": {
    "note": "Shared team credentials - safe for private company repo with trusted coworkers",
    "user_key": "your_pushover_user_key",
    "app_token": "your_pushover_app_token",
    "default_device": "iphone_13_mini",
    "default_sound": "toy_story"
  }
}
```

### Credential Priority
1. **CNS config** (`.claude/automation/cns/config/cns_config.json`) - Primary, git-based
2. **Local override** (`~/.pushover_config`) - Optional, not in git
3. **macOS Keychain** - Legacy fallback

## Command Detection

### Hash Commands (`# APCF:`)
- **Detection**: Prompts starting with `#`
- **Clipboard**: Only first heading line saved
- **Example**: `# APCF: Audit-Proof Commit Format` → `# APCF: Audit-Proof Commit Format`

### Slash Commands (`/apcf`)  
- **Detection**: Prompts starting with `/`
- **Clipboard**: Only command name saved
- **Example**: `/apcf` → `/apcf`

### Natural Language
- **Detection**: All other prompts
- **Clipboard**: Full text saved
- **Example**: `tell me a joke` → `tell me a joke`

## Debug Logging

**Location**: `/tmp/claude_cns_debug.log`

**Key Log Markers**:
- `[CLIPBOARD]` - Clipboard processing events
- `Combined content copied to clipboard` - Success confirmation
- `CNS notification should play automatically` - Audio notification trigger

## System Requirements

**Platform**: Unix-like systems (macOS, Linux)  
**Dependencies**:  
- Common: `jq`  
- Audio (macOS): `afplay` OR Audio (Linux): `paplay`/`aplay`  
- Clipboard (macOS): `pbcopy` OR Clipboard (Linux): `xclip`/`xsel`  
- Text-to-Speech (macOS): `say` OR Speech (Linux): `espeak`/`festival`  
**Shell**: POSIX-compliant shells (zsh, bash)

> **Note**: Uses Unix conventions (`$HOME`, `/tmp/`) - not Windows-compatible

### Audio File Setup

The CNS notification system requires an audio file for notifications:

**Required Location**: `$HOME/.claude/media/toy-story-notification.mp3`

> **⚠️ Important**: You must provide your own notification audio file. Place any `.mp3` audio file at the path above. The system will gracefully handle missing audio files by skipping audio playback while continuing with folder name announcement.

**Setup Example**:
```bash
# Create media directory
mkdir -p "$HOME/.claude/media"

# Add your preferred notification sound (replace with your audio file)
cp /path/to/your/notification.mp3 "$HOME/.claude/media/toy-story-notification.mp3"
```

## Session Metadata

CNS extracts and displays rich metadata from Claude Code hooks:

### Claude Code Native Fields
- `session_id` - Unique session UUID
- `hook_event_name` - Event type (Stop, SessionEnd, etc.)
- `cwd` - Current working directory
- `transcript_path` - Path to conversation JSONL
- `permission_mode` - Permission level

### Derived Context
- `username` - `$USER` or `whoami`
- `hostname` - `hostname -s` (short hostname)
- `folder_name` - `basename` of cwd
- `session_short` - First 8 characters of session_id

## Deployment

### Git-based Workflow
```bash
# On any machine (macOS or Linux)
cd ~/.claude && git pull

# CNS automatically works - no credential setup needed!
# Pushover credentials are in cns_config.json (git-based)
```

### Tools

**Diagnostic**: `cns-diagnose`
- Check CNS system health
- Verify Pushover credentials
- Test connectivity
- Show recent activity

**Remote Setup** (deprecated): `cns-setup-remote-pushover.sh`
- Deploy credentials to remote servers
- Superseded by git-based credentials

**SSH Tunnel** (optional): `cns-tunnel-listener.sh`
- Receive remote notifications via SSH tunnel
- Alternative to Pushover for local-only setup

## Integration

### Claude Code Hooks
**File**: `.claude/settings.json`
```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/.claude/automation/cns/cns_hook_entry.sh"
          }
        ]
      }
    ]
  }
}
```

### Environment Variables
- `CNS_SESSION_ID` - Exported session ID for remote client
- `CNS_HOOK_EVENT` - Exported hook event name
- `CNS_CWD` - Exported working directory
- `CLAUDE_CNS_CLIPBOARD` - Override clipboard functionality

## Audio Configuration

### Volume Control
The CNS notification volume can be adjusted independently of system volume:

**Configuration**: Edit `notification_volume` in `config/cns_config.json`
- `0.0` = Silent (no audio)
- `0.1` = Very quiet (10%)
- `0.3` = Moderate (30%) - **Default setting**
- `0.5` = Half volume (50%)
- `1.0` = Full volume (original loudness)

**Testing**: Use `cns-notify` to test audio playback (note: manual test does not include volume control)

**Important**: This only affects CNS notification audio. System volume and other applications remain unchanged.

## Troubleshooting

### Clipboard Issues (Currently Disabled)
> **Note**: Clipboard functionality is currently disabled (`clipboard_enabled: false`).
To re-enable: Set `"clipboard_enabled": true` in `config/cns_config.json`

### No CNS Notification
- Verify `cns_notification_hook.sh` is executable
- Check that both notification and CNS hooks are configured in settings
- Test manually with `cns-notify` command

### Audio Volume Issues
- Check `notification_volume` setting in `config/cns_config.json`
- Verify `afplay` is available and functional
- Ensure audio file exists: `$HOME/.claude/media/toy-story-notification.mp3`

### Command Detection Issues
- Review `[CLIPBOARD]` log entries for classification results
- Verify command starts with `#` or `/` for proper detection
- Check clipboard content matches expected format

## Legacy Information

Historical migration from specialized text-to-speech system to current notification-focused CNS architecture.