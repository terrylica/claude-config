# CNS (Conversation Notification System)

Intelligent clipboard tracking and audio completion notification for Claude Code responses.

## Architecture Overview

**Major Change**: Renamed from TTS system (2025-07-28). CNS focuses on clipboard conversation tracking and audio notifications.

### Current System (CNS Architecture)
- **Main Script**: `conversation_handler.sh` (168 lines) - Clipboard processing only
- **Configuration**: `config/cns_config.json` - Simplified clipboard and sound settings  
- **Entry Point**: `cns_hook_entry.sh` - Hook system integration
- **CNS Notification**: `cns_notification_hook.sh` - Toy Story audio notification with folder name TTS

## Functionality

### ✅ Active Features
- **Clipboard Tracking**: Copies both user prompts and Claude responses to clipboard
- **Command Detection**: Smart handling of hash (`#`) and slash (`/`) commands
- **CNS Notification**: Toy Story audio notification with folder name TTS when Claude finishes responding
- **Volume Control**: Configurable notification volume (affects only CNS audio, not system volume)
- **Combined Format**: Clipboard contains `USER: [prompt]\n\nCLAUDE: [response]`

### ❌ Removed Features (From Previous TTS System)
- All speech synthesis functionality
- Speech rate, voice, and volume configurations
- Complex paragraph aggregation for audio
- Multi-stage content processing pipelines

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
    "enable_cns_notification": true,
    "tts_removed": true
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
- Text-to-Speech (macOS): `say` OR TTS (Linux): `espeak`/`festival`  
**Shell**: POSIX-compliant shells (zsh, bash)

> **Note**: Uses Unix conventions (`$HOME`, `/tmp/`) - not Windows-compatible

### Audio File Setup

The CNS notification system requires an audio file for notifications:

**Required Location**: `$HOME/.claude/media/toy-story-notification.mp3`

> **⚠️ Important**: You must provide your own notification audio file. Place any `.mp3` audio file at the path above. The system will gracefully handle missing audio files by skipping audio playback while continuing with folder name text-to-speech.

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
- `CLAUDE_CNS_CLIPBOARD=1` - Enable clipboard functionality (default: enabled)

## Audio Configuration

### Volume Control
The CNS notification volume can be adjusted independently of system volume:

**Configuration**: Edit `notification_volume` in `config/cns_config.json`
- `0.0` = Silent (no audio)
- `0.1` = Very quiet (10%)
- `0.3` = Moderate (30%) - **Default setting**
- `0.5` = Half volume (50%)
- `1.0` = Full volume (original loudness)

**Testing**: Use `$HOME/.claude/bin/cns-notify` to test volume level

**Important**: This only affects CNS notification audio. System volume and other applications remain unchanged.

## Troubleshooting

### Empty Clipboard
- Check debug log for `Combined content copied to clipboard` message
- Verify clipboard tool is available: `pbcopy` (macOS), `xclip`/`xsel` (Linux)
- Ensure transcript file is readable and contains valid JSON

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

## Migration Notes

**From TTS System (Renamed to CNS 2025-07-28)**:
- All speech synthesis removed
- Configuration simplified significantly  
- Script size reduced 81% (892 → 168 lines)
- Clipboard functionality enhanced with combined format
- CNS notification preserved as separate system
- Complete file/directory structure renamed for clarity