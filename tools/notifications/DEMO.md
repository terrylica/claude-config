# Pushover Notifications Demo

## Quick Test
```bash
claude-notify "Test Complete" "All systems operational!"
```

## Available Sounds
toy_story, dune, bike, siren, cosmic, alien, vibrate, none

## Usage Examples
```bash
# Claude Code notifications (always toy_story sound)
claude-notify "Build Complete" "Ready to deploy"

# Custom sound notifications  
pushover-notify "Alert" "System issue" "iphone_13_mini" "siren"

# Emergency notifications (retry until acknowledged)
pushover-emergency "URGENT" "Action required!" 30 60 "siren"
```

## Emergency Notifications
- **HARD API LIMIT**: Minimum 30 seconds between retries
- **Confirmed by API**: "retry is too small, must be at least 30 seconds"
- **Maximum duration**: 3 hours (180 minutes)
- **Maximum retries**: 50 attempts

## API Reference
https://pushover.net/api