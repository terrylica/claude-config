# [BUG] "Stop hook error" displayed despite hooks producing zero output (v2.0.28)

## Summary

Claude Code v2.0.28 displays "⎿ Stop hook error" after every response, even though all Stop hooks produce exactly **0 bytes of output** when tested manually. The error persists across fresh sessions despite comprehensive fixes including output redirection, process cleanup, and single-instance protection.

## Environment

- **Claude Code Version**: 2.0.28
- **Platform**: macOS Darwin 24.6.0
- **Terminal**: iTerm.app / iTerm2
- **Installation**: npm global (`~/.claude/local/node_modules/.bin/claude`)
- **Configuration**: `~/.claude/settings.json`

## Bug Description

### Observed Behavior

```
> Tell me a joke

⏺ Why do programmers prefer dark mode?

  Because light attracts bugs! 🐛💡
  ⎿  Stop hook error        <-- ERROR APPEARS EVERY TIME
```

**Error appears**:

- ✅ On every Stop event (end of Claude's response)
- ✅ Across fresh sessions (not cached)
- ✅ In multiple workspaces
- ✅ Even with --debug mode enabled

**Debug log shows**:

```
[DEBUG] Getting matching hook commands for Stop with query: undefined
[DEBUG] Found 1 hook matchers in settings
[DEBUG] Matched 3 unique hooks for query "no match query" (3 before deduplication)
[DEBUG] Hook output does not start with {, treating as plain text
[DEBUG] Hook output does not start with {, treating as plain text
[DEBUG] Hook output does not start with {, treating as plain text
```

### Expected Behavior

Stop hooks should execute silently with **no error message** since they:

1. Produce 0 bytes of output (verified)
1. Exit with code 0
1. Have proper output redirection (`> /dev/null 2>&1 &`)
1. Are configured correctly per documentation

### Actual Behavior

"Stop hook error" appears after every response, despite hooks functioning correctly (they execute, produce no output, and complete successfully).

## Reproduction Steps

### 1. Configure Stop Hooks

`~/.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$HOME/.claude/automation/cns/cns_hook_entry.sh"
          },
          {
            "type": "command",
            "command": "$HOME/.claude/automation/prettier/format-markdown.sh"
          },
          {
            "type": "command",
            "command": "$HOME/.claude/automation/lychee/runtime/hook/check-links-hybrid.sh"
          }
        ]
      }
    ]
  }
}
```

### 2. Create Minimal Test Hook

`/tmp/test-hook.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail

# Background process with output redirection
{
    # All operations redirected
    echo "test" > /dev/null 2>&1
} > /dev/null 2>&1 &

# Exit immediately
exit 0
```

```bash
chmod +x /tmp/test-hook.sh
```

### 3. Verify Hook Produces Zero Output

```bash
$ echo '{}' | /tmp/test-hook.sh 2>&1 | wc -c
0

$ echo '{"session_id":"test","hook_event_name":"Stop"}' | /tmp/test-hook.sh 2>&1 | wc -c
0
```

### 4. Start Claude Code

```bash
$ claude --debug
> Tell me a joke
# ERROR APPEARS: "⎿ Stop hook error"
```

### 5. Check Debug Log

```bash
$ grep "Hook output" ~/.claude/debug/*.txt | tail -5
[DEBUG] Hook output does not start with {, treating as plain text
[DEBUG] Hook output does not start with {, treating as plain text
[DEBUG] Hook output does not start with {, treating as plain text
```

## Verification Tests Conducted

### Test 1: Manual Hook Execution

```bash
$ for hook in cns_hook_entry.sh format-markdown.sh check-links-hybrid.sh; do
    echo "Testing: $hook"
    output=$(echo '{"session_id":"test","hook_event_name":"Stop"}' | "$HOME/.claude/automation/$hook" 2>&1)
    echo "Output size: ${#output} bytes"
done

Testing: cns_hook_entry.sh
Output size: 0 bytes
Testing: format-markdown.sh
Output size: 0 bytes
Testing: check-links-hybrid.sh
Output size: 0 bytes
```

### Test 2: Delayed Output Check

```bash
$ echo '{}' | hook_script.sh > /tmp/out 2>&1
$ sleep 5  # Wait for background processes
$ wc -c < /tmp/out
0
```

### Test 3: Process Inspection

```bash
$ ps aux | grep -E "cns_hook|format-markdown|check-links" | grep -v grep
# No stale processes found
```

### Test 4: File Handle Check

```bash
$ lsof | grep -E "cns_hook|format-markdown|check-links"
# No open file handles to old hook versions
```

## Attempted Fixes (All Verified, None Resolved Issue)

1. ✅ **Added block-level output redirection** to all background processes

   ```bash
   } > /dev/null 2>&1 &
   ```

1. ✅ **Suppressed UV debug output**

   ```bash
   export UV_NO_PROGRESS=1
   export RUST_LOG=error
   ```

1. ✅ **Redirected Python script stdout** (7 locations)

   ```bash
   script.py args >> /dev/null 2>> "$log_file"
   ```

1. ✅ **Added explicit exit 0** to all hooks

1. ✅ **Killed stale cached processes** (24+ hour old bash processes)

1. ✅ **Implemented single-instance protection** (prevents duplicate processes)

1. ✅ **Added stale process cleanup** (auto-kills processes >1 hour old)

## Root Cause Analysis

### Theory 1: Claude Code UI Bug

Claude Code reports "Hook output does not start with {" even when hooks produce **zero bytes of output**. This may be:

- A regression from v2.0.17+ hook display issues (#9602)
- False positive detection
- Race condition in output capture

### Theory 2: SessionStart vs Stop Hook Confusion

Debug logs show 5 errors (2 SessionStart + 3 Stop), but:

- SessionStart hooks **are supposed to output** (inject-results.sh produces 940 bytes for context)
- Stop hooks produce 0 bytes but still trigger error

Claude Code might be incorrectly validating Stop hook output format.

### Theory 3: JSON Output Expectation Mismatch

Error message "Hook output does not start with {" suggests Claude Code expects **JSON output** from Stop hooks, but documentation indicates:

- Hooks can output nothing (exit 0 = success, no output)
- JSON output is **optional** for structured responses
- Plain exit codes are valid

## Related Issues

- #9679 - Hook status messages displayed on every API response (v2.0.19-2.0.20)
- #9602 - Stop Hook Regression in 2.0.17-2.0.20 - Fires Multiple Times
- #10401 - All hooks require --debug flag in v2.0.27
- #9052 - Stop Hooks Causing Unexpected Processing State Interruption

## Impact

- **Severity**: Medium (cosmetic but persistent)
- **User Experience**: Error messages clutter every interaction
- **Functionality**: Hooks work correctly despite error messages
- **Workaround**: None (error appears regardless of fixes)

## Requested Fix

1. **If hooks produce 0 bytes output**, do not show "Stop hook error"
1. **Clarify documentation**: Are Stop hooks required to output JSON?
1. **Fix detection logic**: "Hook output does not start with {" should not trigger for empty output

## Diagnostic Files Available

- Debug logs: `~/.claude/debug/*.txt` (shows "Hook output does not start with {")
- Hook test results: All hooks verified to produce 0 bytes
- Process inspection: No cached processes exist
- Git commits: v0.2.1-cns-output-fix, v0.3.0-single-instance-protection

## Questions for Claude Team

1. Are Stop hooks **required** to output JSON starting with `{`?
1. Should empty output (0 bytes, exit 0) trigger "Stop hook error"?
1. Is this related to the v2.0.17+ hook display regression (#9602)?
1. Can you reproduce with minimal test hook shown above?

---

**Report Date**: 2025-10-27
**Reproducibility**: 100% (consistent across all sessions)
**Blocker**: No (hooks work, error is cosmetic)
**Versions Affected**: v2.0.28 (possibly earlier versions)
