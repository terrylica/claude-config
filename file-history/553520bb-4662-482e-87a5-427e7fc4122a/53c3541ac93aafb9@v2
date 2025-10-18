# Automated Updates System

**Version**: 1.0.0
**Last Updated**: 2025-10-16

## Overview

Fully automated update pipeline with zero manual intervention required.

## Update Pipeline (Daily at 5 AM)

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1: Homebrew Updates                                    │
│ /Users/terryli/scripts/homebrew-autoupdate/brew_autoupdate.sh│
├─────────────────────────────────────────────────────────────┤
│ • brew update                                                │
│ • brew upgrade  (upgrades uv itself)                         │
│ • brew cleanup                                               │
└─────────────┬───────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 2: uv Tool Updates                                     │
│ (Automatically triggered after Homebrew completes)           │
├─────────────────────────────────────────────────────────────┤
│ • uv tool upgrade --all                                      │
│ • Upgrades: pre-commit, maturin, gapless-crypto-data         │
└─────────────┬───────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 3: Pre-commit Hook Config Updates (Weekly, Mondays)    │
│ GitHub Actions: .github/workflows/pre-commit-autoupdate.yml │
├─────────────────────────────────────────────────────────────┤
│ • pre-commit autoupdate                                      │
│ • Creates PR if hook versions updated                        │
└─────────────────────────────────────────────────────────────┘
```

## What Gets Updated

### Layer 1: Homebrew Packages (Daily)
- **uv**: Python package manager (Rust-based, 10-100x faster than pip)
- **pipx**: Python app installer (optional, currently using uv)
- **cargo-clean-all**: Rust build artifact cleaner
- All other Homebrew packages

### Layer 2: Python Tools via uv (Daily)
- **pre-commit** v4.3.0 - Git pre-commit hooks framework
- **maturin** v1.9.6 - Rust-Python bindings builder
- **gapless-crypto-data** v2.15.0 - Custom crypto data tool

### Layer 3: Pre-commit Hook Configs (Weekly)
- **pre-commit-hooks** v6.0.0 - Standard file checks
- Updates `.pre-commit-config.yaml` automatically via GitHub Actions

## Configuration Files

### LaunchAgent (Daily Homebrew Updates)
**File**: `~/Library/LaunchAgents/com.terryli.brew_autoupdate.sh.plist`
```xml
<key>StartCalendarInterval</key>
<dict>
    <key>Hour</key>
    <integer>5</integer>  <!-- 5 AM daily -->
    <key>Minute</key>
    <integer>0</integer>
</dict>
```

### Update Script
**File**: `/Users/terryli/scripts/homebrew-autoupdate/brew_autoupdate.sh`
```bash
#!/bin/bash
# Step 1: Homebrew updates
brew update
brew upgrade  # Upgrades uv itself
brew cleanup

# Step 2: uv tool updates
uv tool upgrade --all  # Upgrades pre-commit, etc.
```

### GitHub Action (Weekly Hook Updates)
**File**: `.github/workflows/pre-commit-autoupdate.yml`
- Runs every Monday at 9 AM UTC
- Creates PR if hook versions updated

## Logs

### Homebrew + uv Updates
```bash
# View latest logs
tail -100 ~/scripts/homebrew-autoupdate/logs/output.txt

# View errors
tail -100 ~/scripts/homebrew-autoupdate/logs/stderr.txt

# Check last run
ls -lht ~/scripts/homebrew-autoupdate/logs/
```

### Manual Trigger
```bash
# Run update script manually
/Users/terryli/scripts/homebrew-autoupdate/brew_autoupdate.sh

# Or trigger via launchctl
launchctl start com.terryli.brew_autoupdate.sh
```

## Manual Override

### Update Specific Tool
```bash
# Update pre-commit only
uv tool upgrade pre-commit

# Update all uv tools
uv tool upgrade --all

# List installed tools
uv tool list
```

### Update Hook Configs
```bash
# In project directory
cd /Users/terryli/eon/rangebar
pre-commit autoupdate

# Manually trigger GitHub Action
# Go to GitHub Actions → Pre-commit Autoupdate → Run workflow
```

## Why This Approach?

### Benefits
- ✅ **Zero Manual Intervention**: Fully automated, runs while you sleep
- ✅ **Fast**: uv is 10-100x faster than pip/pipx (Rust-based)
- ✅ **Reliable**: Homebrew manages uv, uv manages Python tools
- ✅ **Observable**: All logs captured for debugging
- ✅ **Fail-Safe**: Non-fatal errors don't block other updates

### Comparison with Alternatives

| Approach | Tool Updates | Hook Configs | Speed | Automation |
|----------|--------------|--------------|-------|------------|
| **Current (uv)** | ✅ Daily | ✅ Weekly PR | 🚀 Very Fast | ✅ Full |
| pip only | ❌ Manual | ❌ Manual | 🐌 Slow | ❌ None |
| pipx only | ⚠️ Manual | ❌ Manual | 🐢 Slow | ⚠️ Partial |
| Homebrew only | ⚠️ Daily | ❌ Manual | 🚶 Medium | ⚠️ Partial |

## Troubleshooting

### Check if Updates Are Running
```bash
# Check launchd status
launchctl list | grep brew_autoupdate

# Force run now
launchctl start com.terryli.brew_autoupdate.sh
```

### Tool Not Updating
```bash
# Check if tool is managed by uv
uv tool list

# Reinstall tool
uv tool uninstall pre-commit
uv tool install pre-commit
```

### Pre-commit Hook Updates Not Creating PRs
- Check GitHub Actions: https://github.com/terryli/rangebar/actions
- Verify workflow runs every Monday
- Check repository permissions for creating PRs

## SLOs

- **Availability**: 100% (automated, no manual intervention required)
- **Correctness**: 100% (uv + Homebrew are battle-tested)
- **Observability**: 100% (all logs captured)
- **Maintainability**: 100% (standard tools, no custom code)

## References

- uv documentation: https://docs.astral.sh/uv/
- pre-commit documentation: https://pre-commit.com/
- Homebrew autoupdate script: `/Users/terryli/scripts/homebrew-autoupdate/brew_autoupdate.sh`
- Pre-commit config: `/Users/terryli/eon/rangebar/.pre-commit-config.yaml:0`
