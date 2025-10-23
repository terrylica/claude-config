# Session Recovery & Troubleshooting

Source: `docs/standards/CLAUDE_SESSION_STORAGE_STANDARD.md` (verified 2025-08-12)

---

## ✅ Successful Recovery Process

**Context**: Migrated 633+ sessions from custom `~/.claude/system/sessions/` structure to official `~/.claude/projects/` format.

**Recovery Steps**:

1. Removed legacy symlink: `rm ~/.claude/projects` (was pointing to `system/sessions`)
2. Created official directory: `mkdir -p ~/.claude/projects`
3. Migrated all sessions with timestamp preservation using custom recovery script
4. Result: All sessions properly organized in official format

---

## 🚨 Critical Pitfall: HOME Environment Variable

**Problem**: Claude may write sessions to wrong location if `$HOME` is incorrect.

**Symptoms**:

- `claude -r` shows "No conversations found to resume"
- New conversations work but don't create session files in expected location
- Sessions may be created in `/tmp/` or other unexpected directories

**Root Cause**: Environment variable `HOME` set to wrong path (e.g., `/tmp/clean-claude-test` instead of `/home/username`)

**Diagnosis Commands**:

```bash
# Check current HOME
echo "HOME: $HOME"

# Check expected HOME
echo "Expected: $(getent passwd $(whoami) | cut -d: -f6)"

# Find where Claude is actually writing
find /tmp -name "*.jsonl" -path "*/.claude/projects/*" 2>/dev/null
find ~ -name "*.jsonl" -path "*/.claude/projects/*" 2>/dev/null
```

**Solution**:

```bash
# Fix environment in current shell
export HOME=/home/$(whoami)

# Test Claude session creation
echo "test" | claude --dangerously-skip-permissions --model sonnet
```

**Prevention**: Check IDE/terminal settings (Cursor, VS Code) that may override HOME variable.

---

## 🔍 Session Creation Troubleshooting

**If Claude isn't creating sessions**:

### 1. Check Authentication

```bash
claude /login
```

### 2. Verify HOME Variable

```bash
echo "HOME: $HOME"
# Should be: /home/username
```

### 3. Check Disk Space & Permissions

```bash
df -h ~/.claude
ls -ld ~/.claude/projects/
touch ~/.claude/projects/test-write.tmp && rm ~/.claude/projects/test-write.tmp
```

### 4. Monitor File Creation

```bash
# Before conversation
find ~/.claude/projects -name "*.jsonl" | wc -l

# Start conversation, then check again
find ~/.claude/projects -name "*.jsonl" | wc -l
```

### 5. Check Alternative Locations

```bash
# Find sessions created in last hour
find /tmp -name "*.jsonl" -path "*/.claude/projects/*" -newermt "1 hour ago" 2>/dev/null
```

---

## 📋 Session Resume Behavior

**"No conversations found to resume"** can mean:

- Sessions exist but are marked as "complete" (normal)
- Sessions exist but have wrong timestamps/format
- Sessions are in wrong location due to HOME variable issue
- No valid resumable sessions (sessions need assistant responses to be resumable)

**Verification**:

```bash
# Count total sessions
find ~/.claude/projects -name "*.jsonl" -type f | wc -l

# Check recent sessions
find ~/.claude/projects -name "*.jsonl" -type f -newermt "1 day ago"

# Verify session format
head -n 1 ~/.claude/projects/*/*.jsonl | python -m json.tool
```

---

## 🛠️ Recovery Script Reference

Created `/home/tca/.claude/tools/session-recovery.sh` for systematic session migration:

- Handles multiple session directory formats
- Preserves timestamps and metadata
- Maps platform-specific paths to official format
- Safe to run multiple times (idempotent)

---

## 🎯 Key Learnings

1. **Official format works perfectly** - Docker test confirmed `~/.claude/projects/` is correct
2. **Environment matters more than file structure** - Wrong HOME breaks everything
3. **IDE terminals can override environment** - Check Cursor/VS Code settings
4. **Sessions are resumable only if incomplete** - Completed sessions won't show in `claude -r`
5. **Original wrapper is sufficient** - No custom wrapper needed, just fix environment
