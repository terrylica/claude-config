# Pushover Notifications Demo

## CNS Automatic Notifications

CNS automatically sends Pushover notifications when Claude Code completes responses.

**Notification Format:**

```
Title: CNS: terryli@Terrys-MacBook-Pro
Message:
  📁 project-folder
  Response preview (first 200 chars)

  🆔 b31bc615 | Stop
```

**Session Metadata Included:**

- Username@hostname (identifies which machine)
- Folder name (current project)
- Session ID (track conversations)
- Hook event (Stop, SessionEnd, etc.)

## Manual Testing

**Quick Test:**

```bash
pushover-notify "Test Complete" "All systems operational!"
```

**With Context:**

```bash
pushover-notify "Test" "With metadata" "" "" --with-context
```

**Available Sounds:**
toy_story, dune, bike, siren, cosmic, alien, vibrate, none

## Usage Examples

**Basic notification:**

```bash
pushover-notify "Build Complete" "Ready to deploy"
```

**Custom sound:**

```bash
pushover-notify "Alert" "System issue" "iphone_13_mini" "siren"
```

**Emergency (retry until acknowledged):**

```bash
pushover-emergency "URGENT" "Action required!" 30 60 "siren"
```

## Credential Sources

Pushover credentials are loaded with priority:

1. `.claude/automation/cns/config/cns_config.json` (git-based, team-shared)
2. `~/.pushover_config` (local override)
3. macOS Keychain (legacy)

## Emergency Notifications

- Minimum 30 seconds between retries (API limit)
- Maximum duration: 3 hours (180 minutes)
- Maximum retries: 50 attempts

## API Reference

https://pushover.net/api
