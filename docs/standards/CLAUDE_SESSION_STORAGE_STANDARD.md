# Claude Code Session Storage: Verified Standard (2025-08-12)

This document records definitive, empirical evidence for how official Claude Code stores sessions, and how our workspace deviated from it. It replaces assumptions with proof.

## Summary (Authoritative)

- Official location: `$HOME/.claude/projects/`
- Per-workspace folders: encoded absolute path of CWD (slashes → hyphens)
- File format: JSONL, one event per line, UUID filenames
- Confirmed by fully isolated Docker test (Ubuntu 24.04 + npm global install)

## Empirical Evidence

We ran a clean, isolated test:

1. Built Docker image (Ubuntu 24.04), installed Node.js and `@anthropic-ai/claude-code` globally.
2. Created user `testuser`, ran `claude` in `/home/testuser/my-project`.
3. Results inside container (key excerpts):

```
$HOME/.claude/
  projects/
    -home-testuser-my-project/
      364695f1-13e7-4cbb-ad4b-0eb416feb95d.jsonl
  statsig/
  shell-snapshots/
  todos/
```

Therefore, official Claude Code stores sessions under `~/.claude/projects/` using encoded path directories.

## Our Previous Deviation (Explained)

- Historical symlinks existed in `~/.claude`:
  - `projects -> system/sessions` (removed)
  - `ide -> system/ide`, `statsig -> system/statsig`, `todos -> system/todos`
- Active sessions lived in `~/.claude/system/sessions/…` (non-standard), and tooling referenced that path.
- This customization caused path confusion and tooling failures (e.g., SAGE), masking the official behavior.

## Why We Are Certain

- Reproduced behavior in a hermetic Docker container.
- No host config, no local aliases, no symlinks: pure upstream behavior.
- Observed creation of `projects/` and an encoded per-project folder with a `.jsonl` session file.

## Migration Guidance

- Preferred: Align to the official standard and write tools against `~/.claude/projects/`.
- If custom layout is retained, ensure tools resolve `~/.claude/projects/` faithfully (avoid symlink surprises).
- For cross-host sync, mirror `~/.claude/projects/` and preserve timestamps.

## Verification Commands

```bash
ls -la ~/.claude/projects/
find ~/.claude/projects/ -name "*.jsonl" -type f | head -5
head -n 1 ~/.claude/projects/*/*.jsonl | python -m json.tool
```

## Decision

Adopt `~/.claude/projects/` as the authoritative session root. Update internal docs, tools, and scripts to treat it as the single source of truth.

Implementation plan: `specifications/session-storage-adoption.yaml`

## Session Recovery & Troubleshooting (2025-08-12)

### ✅ Successful Recovery Process

**Context**: Migrated 633+ sessions from custom `~/.claude/system/sessions/` structure to official `~/.claude/projects/` format.

**Recovery Steps**:
1. Removed legacy symlink: `rm ~/.claude/projects` (was pointing to `system/sessions`)
2. Created official directory: `mkdir -p ~/.claude/projects`
3. Migrated all sessions with timestamp preservation using custom recovery script
4. Result: All sessions properly organized in official format

### 🚨 Critical Pitfall: HOME Environment Variable

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

### 🔍 Session Creation Troubleshooting

**If Claude isn't creating sessions**:

1. **Check Authentication**:
   ```bash
   claude /login
   ```

2. **Verify HOME Variable**:
   ```bash
   echo "HOME: $HOME"
   # Should be: /home/username
   ```

3. **Check Disk Space & Permissions**:
   ```bash
   df -h ~/.claude
   ls -ld ~/.claude/projects/
   touch ~/.claude/projects/test-write.tmp && rm ~/.claude/projects/test-write.tmp
   ```

4. **Monitor File Creation**:
   ```bash
   # Before conversation
   find ~/.claude/projects -name "*.jsonl" | wc -l
   
   # Start conversation, then check again
   find ~/.claude/projects -name "*.jsonl" | wc -l
   ```

5. **Check Alternative Locations**:
   ```bash
   # Find sessions created in last hour
   find /tmp -name "*.jsonl" -path "*/.claude/projects/*" -newermt "1 hour ago" 2>/dev/null
   ```

### 📋 Session Resume Behavior

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

### 🛠️ Recovery Script Reference

Created `/home/tca/.claude/tools/session-recovery.sh` for systematic session migration:
- Handles multiple session directory formats
- Preserves timestamps and metadata
- Maps platform-specific paths to official format
- Safe to run multiple times (idempotent)

### 🎯 Key Learnings

1. **Official format works perfectly** - Docker test confirmed `~/.claude/projects/` is correct
2. **Environment matters more than file structure** - Wrong HOME breaks everything
3. **IDE terminals can override environment** - Check Cursor/VS Code settings
4. **Sessions are resumable only if incomplete** - Completed sessions won't show in `claude -r`
5. **Original wrapper is sufficient** - No custom wrapper needed, just fix environment

