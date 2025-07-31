# CNS (Conversation Notification System)

Audio completion notification for Claude Code responses (clipboard currently disabled).

## Architecture Overview

CNS provides audio notifications when Claude Code completes responses, with configurable clipboard functionality.

### Current System (CNS Architecture)
- **Main Script**: `conversation_handler.sh` (207 lines) - Clipboard processing and coordination
- **Configuration**: `config/cns_config.json` - System settings (clipboard disabled)  
- **Entry Point**: `cns_hook_entry.sh` - Async hook entry point
- **CNS Notification**: `cns_notification_hook.sh` - Audio notification with folder name text-to-speech

## Functionality

### ✅ Active Features
- **Audio Notification**: Audio file playback with configurable volume when Claude finishes responding
- **Text-to-Speech**: Folder name announcement with tmux context detection
- **Volume Control**: Configurable notification volume (affects only CNS audio, not system volume)
- **Async Processing**: Fire-and-forget background processing for session performance

### ❌ Currently Disabled Features
- **Clipboard Tracking**: Currently disabled (`clipboard_enabled: false` in config)
- **Command Detection**: Preserved but not active due to disabled clipboard
- **Combined Format**: Not active due to disabled clipboard

## Configuration

**File**: `config/cns_config.json`

```json
{
  "note": "CNS (Conversation Notification System) - clipboard and notification only",
  "command_detection": {
    "enabled": true,
    "hash_commands": {
      "description": "Commands starting with # (e.g., # APCF:)",
      "clipboard_mode": "first_line_only"
    },
    "slash_commands": {
      "description": "Commands starting with / (e.g., /apcf)",
      "clipboard_mode": "command_name_only"
    },
    "natural_language": {
      "description": "Regular user prompts",
      "clipboard_mode": "full_text"
    }
  },
  "features": {
    "enable_clipboard_debug": true,
    "enable_cns_notification": true
  },
  "audio": {
    "notification_volume": 0.3,
    "volume_note": "Volume level for notification audio (0.0 = silent, 1.0 = full volume)"
  }
}
```

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
            "command": "$HOME/.claude/automation/cns/cns_notification_hook.sh"
          },
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
- `CLAUDE_CNS_CLIPBOARD=1` - Override clipboard functionality (set by cns_hook_entry.sh)

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