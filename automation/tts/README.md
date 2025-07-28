# Clipboard & Glass Sound Hook System

Intelligent clipboard tracking and audio completion notification for Claude Code responses.

## Architecture Overview

**Major Change**: TTS functionality completely removed (2025-07-28). System now focused on clipboard conversation tracking and glass sound notifications.

### Current System (Post-TTS Removal)
- **Main Script**: `claude_response_speaker.sh` (168 lines) - Clipboard + glass sound only
- **Configuration**: `config/tts_config.json` - Simplified clipboard and sound settings  
- **Entry Point**: `tts_hook_entry.sh` - Hook system integration
- **Glass Sound**: `glass_sound_wrapper.sh` - Separate audio notification system

## Functionality

### ✅ Active Features
- **Clipboard Tracking**: Copies both user prompts and Claude responses to clipboard
- **Command Detection**: Smart handling of hash (`#`) and slash (`/`) commands
- **Glass Sound**: Audio notification when Claude finishes responding
- **Combined Format**: Clipboard contains `USER: [prompt]\n\nCLAUDE: [response]`

### ❌ Removed Features  
- All TTS/speech synthesis functionality
- Speech rate, voice, and volume configurations
- Complex paragraph aggregation for audio
- Multi-stage content processing pipelines

## Configuration

**File**: `config/tts_config.json`

```json
{
  "note": "TTS functionality removed - now clipboard and glass sound only",
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
    "enable_glass_sound": true,
    "tts_removed": true
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

**Location**: `/tmp/claude_tts_debug.log`

**Key Log Markers**:
- `[CLIPBOARD]` - Clipboard processing events
- `Combined content copied to clipboard` - Success confirmation
- `Glass sound should play automatically` - Audio notification trigger

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
            "command": "/Users/terryli/.claude/automation/tts/glass_sound_wrapper.sh"
          },
          {
            "type": "command", 
            "command": "/Users/terryli/.claude/automation/tts/tts_hook_entry.sh"
          }
        ]
      }
    ]
  }
}
```

### Environment Variables
- `CLAUDE_TTS_TO_CLIPBOARD=1` - Enable clipboard functionality (default: enabled)

## Troubleshooting

### Empty Clipboard
- Check debug log for `Combined content copied to clipboard` message
- Verify `pbcopy` is available and functional
- Ensure transcript file is readable and contains valid JSON

### No Glass Sound
- Verify `glass_sound_wrapper.sh` is executable
- Check that both glass and TTS hooks are configured in settings

### Command Detection Issues
- Review `[CLIPBOARD]` log entries for classification results
- Verify command starts with `#` or `/` for proper detection
- Check clipboard content matches expected format

## Migration Notes

**From TTS System (Pre-2025-07-28)**:
- All speech synthesis removed
- Configuration simplified significantly  
- Script size reduced 81% (892 → 168 lines)
- Clipboard functionality enhanced with combined format
- Glass sound preserved as separate system