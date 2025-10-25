# Quick Start: Phase 0 Execution

**Run these commands in your terminal (not through Claude Code)**

## Step 1: Authenticate with Telegram

```bash
cd /Users/terryli/.claude/automation/lychee
doppler run -p claude-config -c dev -- uv run auth-telegram.py
```

**When prompted:**

1. `Enter confirmation code:` → Enter the code sent to your Telegram app
2. If prompted: `Enter your password:` → Enter your 2FA password

**Success indicator:**

```
✅ Authentication Successful
Session saved to: telegram_session.session
```

## Step 2: Create Bot (After Authentication)

```bash
cd /Users/terryli/.claude/automation/lychee
doppler run -p claude-config -c dev -- uv run create-bot-automated.py
```

**What happens:**

- Connects to Telegram as your user account
- Sends `/newbot` to @BotFather
- Creates bot: "Lychee Link Autofix Bot" (@lychee_link_autofix_bot)
- Extracts token and stores in Doppler
- Gets chat ID and stores in Doppler

**Success indicator:**

```
✅ Bot Creation Successful
Bot Token: 1234567890:... (stored in Doppler)
Chat ID: 123456789 (stored in Doppler)
```

## Step 3: Verify Credentials

```bash
doppler secrets get TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID -p claude-config -c dev
```

**Expected output:**

```
TELEGRAM_BOT_TOKEN: 1234567890:ABCdef...
TELEGRAM_CHAT_ID: 123456789
```

## Troubleshooting

**Problem: "EOF when reading a line"**

- Cause: Running through Claude Code instead of your terminal
- Solution: Run commands directly in Terminal.app, iTerm2, or Ghostty

**Problem: "Session already exists"**

- Type `yes` to overwrite
- Or manually delete: `rm telegram_session.session`

**Problem: "Bot username already taken"**

- Edit `/Users/terryli/.claude/automation/lychee/create-bot-automated.py`
- Change line: `BOT_USERNAME = "lychee_link_autofix_bot"`
- Try: `lychee_link_autofix_bot_2` or similar

**Problem: "Invalid confirmation code"**

- Request new code (it expires quickly)
- Re-run Step 1

## Files Created

After successful execution:

```
/Users/terryli/.claude/automation/lychee/
└── telegram_session.session    (Pyrogram session file)

Doppler (claude-config/dev):
├── TELEGRAM_API_ID             (already stored)
├── TELEGRAM_API_HASH           (already stored)
├── TELEGRAM_BOT_TOKEN          (created by Step 2)
└── TELEGRAM_CHAT_ID            (created by Step 2)
```

## Next Phase

After Phase 0 completes:

- Phase 1: Webhook setup (ngrok tunnel)
- Phase 2: Link detection (stop hook)
- Phase 3: Telegram notifications
- Phase 4: Mobile approval workflow
- Phase 5: Auto-fix execution

## Help

If stuck, return to Claude Code and describe the error message.
