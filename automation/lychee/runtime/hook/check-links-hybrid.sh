#!/usr/bin/env bash
# Lychee Link Validation Stop Hook - Hybrid Pattern
# Version: 0.1.0
# Spec: ~/.claude/specifications/lychee-link-validation.yaml
#
# Execution pattern:
# - TIER 1: Full background check (all .md files, async)
# - TIER 2: Modified files check (selective blocking, sync)
# - Infinite loop prevention via stop_hook_active guard
#
# SLOs:
# - Availability: 99.9% (hook must execute on every stop)
# - Correctness: 100% (no false positives/negatives)
# - Exit time: < 10ms (user-facing requirement)

set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================

config_file="$HOME/.claude/.lycheerc.toml"
log_file="$HOME/.claude/logs/lychee.log"
# Note: Results file must be inside workspace for Claude CLI access
full_results=""  # Will be set after workspace_dir is determined

# =============================================================================
# Read Hook Input & Environment
# =============================================================================

# Read JSON input from stdin (may be empty if Claude Code doesn't provide it)
hook_input=$(cat) || hook_input=""

# Log environment variables for debugging
{
    echo ""
    echo "=========================================================================="
    echo "[$(date +%Y-%m-%d\ %H:%M:%S)] 🔍 ENVIRONMENT VARIABLES"
    echo "=========================================================================="
    echo "CLAUDE_WORKSPACE_DIR=${CLAUDE_WORKSPACE_DIR:-<not set>}"
    echo "PWD=$PWD"
    echo "HOME=$HOME"
    echo "CLAUDE_FILE_PATHS=${CLAUDE_FILE_PATHS:-<not set>}"
    echo ""
    echo "stdin length: ${#hook_input} bytes"
    echo "=========================================================================="
    echo ""
} >> "$log_file" 2>&1

# Determine workspace directory with smart fallback
# Priority: CLAUDE_WORKSPACE_DIR > cwd from JSON > $HOME/.claude
if [[ -n "${CLAUDE_WORKSPACE_DIR:-}" ]]; then
    workspace_dir="$CLAUDE_WORKSPACE_DIR"
elif [[ -n "$hook_input" ]]; then
    workspace_dir=$(echo "$hook_input" | jq -r '.cwd // ""' 2>/dev/null)
    if [[ -z "$workspace_dir" ]]; then
        workspace_dir="$HOME/.claude"
    fi
else
    # Fallback: Assume user's main Claude workspace
    workspace_dir="$HOME/.claude"
fi

# Parse stop_hook_active flag (infinite loop prevention)
if [[ -n "$hook_input" ]]; then
    stop_hook_active=$(echo "$hook_input" | jq -r '.stop_hook_active // false' 2>/dev/null) || stop_hook_active="false"
else
    stop_hook_active="false"
fi

# Extract or generate session ID
if [[ -n "$hook_input" ]]; then
    session_id=$(echo "$hook_input" | jq -r '.session_id // ""' 2>/dev/null)
fi
if [[ -z "${session_id:-}" ]]; then
    # Generate session ID from timestamp if not provided
    session_id="session-$(date +%Y%m%d-%H%M%S)-$$"
fi

# Generate or reuse correlation ID for distributed tracing
if [[ -z "${CORRELATION_ID:-}" ]]; then
    CORRELATION_ID=$("$HOME/.claude/automation/lychee/runtime/lib/ulid_gen.py")
    export CORRELATION_ID
fi

# Compute workspace hash for event tracking
workspace_hash=$(echo -n "$workspace_dir" | sha256sum | cut -c1-8)

# Set results file path inside workspace (required for Claude CLI access)
full_results="$workspace_dir/.lychee-results.txt"

# ============================================================================
# EXTENSIVE LOGGING - Natural Trigger Test
# ============================================================================
{
    echo ""
    echo "=========================================================================="
    echo "[$(date +%Y-%m-%d\ %H:%M:%S)] 🚀 STOP HOOK TRIGGERED"
    echo "=========================================================================="
    echo "Workspace: $workspace_dir"
    echo "Session ID: $session_id"
    echo "Correlation ID: $CORRELATION_ID"
    echo "Workspace Hash: $workspace_hash"
    echo "Stop Hook Active: $stop_hook_active"
    echo "PID: $$"
    echo ""
    echo "Hook input received:"
    echo "$hook_input" | jq '.' 2>/dev/null || echo "$hook_input"
    echo "=========================================================================="
    echo ""
} >> "$log_file" 2>&1

# =============================================================================
# Event Logging - Hook Started
# =============================================================================

"$HOME/.claude/automation/lychee/runtime/lib/event_logger.py" \
    "$CORRELATION_ID" \
    "$workspace_hash" \
    "$session_id" \
    "hook" \
    "hook.started" \
    "{\"workspace_path\": \"$workspace_dir\", \"pid\": $$, \"stop_hook_active\": \"$stop_hook_active\"}" \
    2>> "$log_file" || {
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ❌ Failed to log hook.started event" >> "$log_file" 2>&1
        exit 1
    }

# =============================================================================
# Infinite Loop Prevention
# =============================================================================

# If already continuing from previous stop hook, ALWAYS allow stop
if [[ "$stop_hook_active" == "true" ]]; then
    {
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ⏭️  STOP_HOOK_ACTIVE=true → Allowing stop (loop prevention)"
    } >> "$log_file" 2>&1

    # Log skip event
    "$HOME/.claude/automation/lychee/runtime/lib/event_logger.py" \
        "$CORRELATION_ID" \
        "$workspace_hash" \
        "$session_id" \
        "hook" \
        "hook.skipped_loop_prevention" \
        "{\"reason\": \"stop_hook_active=true\"}" \
        2>> "$log_file" || true

    exit 0
fi

# Check if we're inside an auto-fix workflow (prevents feedback loop)
autofix_state_file="$HOME/.claude/automation/lychee/state/autofix-in-progress.json"
if [[ -f "$autofix_state_file" ]]; then
    # Check if state file is stale (> 10 minutes old)
    state_age=$(( $(date +%s) - $(stat -f %m "$autofix_state_file" 2>/dev/null || echo 0) ))
    if [[ $state_age -lt 600 ]]; then
        {
            echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ⏭️  Auto-fix in progress → Skipping notification (preventing feedback loop)"
            echo "   → State file age: ${state_age}s"
            cat "$autofix_state_file" | jq '.' 2>/dev/null | sed 's/^/   → /'
        } >> "$log_file" 2>&1

        # Log skip event
        "$HOME/.claude/automation/lychee/runtime/lib/event_logger.py" \
            "$CORRELATION_ID" \
            "$workspace_hash" \
            "$session_id" \
            "hook" \
            "hook.skipped_loop_prevention" \
            "{\"reason\": \"autofix_in_progress\", \"state_age_seconds\": $state_age}" \
            2>> "$log_file" || true

        exit 0
    else
        {
            echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ⚠️  Stale auto-fix state file detected (age: ${state_age}s)"
            echo "   → Removing stale state file and continuing"
        } >> "$log_file" 2>&1
        rm -f "$autofix_state_file"
    fi
fi

{
    echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ✓ Loop prevention check passed (stop_hook_active=false, no auto-fix in progress)"
} >> "$log_file" 2>&1

# =============================================================================
# TIER 1: Full Background Validation (Non-blocking)
# =============================================================================

{
    {
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] 🔍 TIER 1: Starting background validation"
        echo "   → Finding markdown files in: $workspace_dir"
    } >> "$log_file" 2>&1

    # Find all markdown files excluding patterns
    markdown_files=$(find "$workspace_dir" -type f -name "*.md" \
        -not -path "*/node_modules/*" \
        -not -path "*/.git/*" \
        -not -path "*/file-history/*" \
        -not -path "*/plugins/marketplaces/*" \
        -not -path "*/todos/*" \
        -not -path "*/.venv/*" 2>/dev/null || true)

    if [[ -n "$markdown_files" ]]; then
        markdown_count=$(echo "$markdown_files" | wc -l | tr -d ' ')
        {
            echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ✓ Found $markdown_count markdown files"
            echo "   → Running lychee validation..."
            echo "   → Config: $config_file"
            echo "   → Output: $full_results"
        } >> "$log_file" 2>&1

        # Run lychee with markdown format for human readability
        env RUST_LOG= lychee \
            --config "$config_file" \
            --format markdown \
            $markdown_files \
            > "$full_results" 2>&1 || true

        # Generate JSON output for programmatic parsing (progressive disclosure)
        json_results="${full_results%.txt}.json"
        env RUST_LOG= lychee \
            --config "$config_file" \
            --format json \
            $markdown_files \
            > "$json_results" 2>&1 || true

        # Log completion with timestamp and summary
        {
            echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ✓ Lychee validation completed"
            echo "   → Results written to: $full_results"
            echo "   → Summary line:"
            tail -1 "$full_results" 2>/dev/null || echo "     (No summary line found)"
        } >> "$log_file" 2>&1

        # Emit notification request for multi-workspace bot
        # Extract error count from lychee results (look for "🚫 Errors" line)
        error_count=$(grep '🚫 Errors' "$full_results" | grep -oE '[0-9]+' | head -1 || echo "0")

        {
            echo "[$(date +%Y-%m-%d\ %H:%M:%S)] 📊 Error count extracted: $error_count"
        } >> "$log_file" 2>&1

        # Parse error_map from JSON for file-level breakdown (progressive disclosure)
        file_error_map=""
        if [[ -f "$json_results" ]]; then
            file_error_map=$(jq -r '.error_map | to_entries[] | "\(.key):\(.value | length)"' "$json_results" 2>/dev/null || echo "")
            {
                echo "[$(date +%Y-%m-%d\ %H:%M:%S)] 📋 File-level error breakdown:"
                echo "$file_error_map" | sed 's/^/   → /'
            } >> "$log_file" 2>&1
        fi

        # Only notify if errors found
        if [[ "$error_count" -gt 0 ]]; then
            {
                echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ⚠️  Errors detected → Emitting notification"
                echo "   → Workspace hash: $workspace_hash"
                echo "   → Session ID: $session_id"
                echo "   → Error count: $error_count"
            } >> "$log_file" 2>&1

            # Create notification request
            notification_file="$HOME/.claude/automation/lychee/state/notifications/notify_${session_id}_${workspace_hash}.json"

            {
                echo "   → Notification file: $notification_file"
            } >> "$log_file" 2>&1

            # Prepare error_details as JSON string (for progressive disclosure)
            error_details_json=$(echo "$file_error_map" | jq -Rs '.' 2>/dev/null || echo '""')

            cat > "$notification_file" <<EOF
{
  "workspace_path": "$workspace_dir",
  "session_id": "$session_id",
  "error_count": $error_count,
  "details": "Found $error_count broken link(s) in workspace",
  "error_details": $error_details_json,
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "correlation_id": "$CORRELATION_ID"
}
EOF

            {
                echo "[$(date +%Y-%m-%d\ %H:%M:%S)] 📤 Notification file written successfully"
                echo "   → File size: $(ls -lh "$notification_file" | awk '{print $5}')"
                echo "   → File content:"
                cat "$notification_file" | sed 's/^/     /'
            } >> "$log_file" 2>&1

            # Log notification created event
            "$HOME/.claude/automation/lychee/runtime/lib/event_logger.py" \
                "$CORRELATION_ID" \
                "$workspace_hash" \
                "$session_id" \
                "hook" \
                "notification.created" \
                "{\"error_count\": $error_count, \"notification_file\": \"$notification_file\"}" \
                2>> "$log_file" || {
                    echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ❌ Failed to log notification.created event" >> "$log_file" 2>&1
                    exit 1
                }

            # Start Telegram bot if not already running (PID file check)
            pid_file="$HOME/.claude/automation/lychee/state/bot.pid"
            bot_script="$HOME/.claude/automation/lychee/runtime/bot/multi-workspace-bot.py"
            bot_running=false

            {
                echo ""
                echo "[$(date +%Y-%m-%d\ %H:%M:%S)] 🔍 Checking if Telegram bot is running..."
            } >> "$log_file" 2>&1

            # Check if PID file exists
            if [[ -f "$pid_file" ]]; then
                bot_pid=$(cat "$pid_file" 2>/dev/null)

                {
                    echo "   → PID file exists: $pid_file (PID: $bot_pid)"
                } >> "$log_file" 2>&1

                # Check if process is alive
                if kill -0 "$bot_pid" 2>/dev/null; then
                    # Verify it's our bot process
                    if ps -p "$bot_pid" -o command= | grep -q "multi-workspace-bot.py"; then
                        bot_running=true
                        {
                            echo "   → ✅ Bot is running (PID: $bot_pid)"
                        } >> "$log_file" 2>&1
                    else
                        {
                            echo "   → ⚠️  PID $bot_pid is not our bot (PID reused), removing stale PID file"
                        } >> "$log_file" 2>&1
                        rm -f "$pid_file"
                    fi
                else
                    {
                        echo "   → ⚠️  Process $bot_pid is dead, removing stale PID file"
                    } >> "$log_file" 2>&1
                    rm -f "$pid_file"
                fi
            else
                {
                    echo "   → PID file does not exist"
                } >> "$log_file" 2>&1
            fi

            # Start bot if not running
            if [[ "$bot_running" == "false" ]]; then
                {
                    echo "   → 🚀 Starting Telegram bot in background..."
                } >> "$log_file" 2>&1

                # Start bot in background with Doppler secrets and output redirected to bot log
                # Note: Doppler CLI injects secrets as environment variables
                nohup doppler run --project claude-config --config dev -- "$bot_script" >> "$HOME/.claude/logs/telegram-handler.log" 2>&1 &
                new_bot_pid=$!

                {
                    echo "   → ✅ Bot started (PID: $new_bot_pid)"
                    echo "   → Bot will auto-shutdown after 10 minutes idle"
                } >> "$log_file" 2>&1
            fi

        else
            {
                echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ✅ No errors found → No notification needed"
            } >> "$log_file" 2>&1
        fi
    else
        {
            echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ⚠️  No markdown files found in $workspace_dir"
        } >> "$log_file" 2>&1
    fi

    {
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] 🏁 TIER 1: Background validation complete"
    } >> "$log_file" 2>&1
} &

# =============================================================================
# TIER 2: Modified Files Validation (Selective Blocking)
# =============================================================================

# Only proceed if:
# 1. CLAUDE_FILE_PATHS is set (files were modified this session)
# 2. Contains at least one .md file
# 3. stop_hook_active is false (already checked above)

if [[ -n "${CLAUDE_FILE_PATHS:-}" ]]; then
    # Extract only markdown files from modified paths
    modified_md_files=$(echo "$CLAUDE_FILE_PATHS" | tr ' ' '\n' | grep '\.md$' 2>/dev/null || true)

    if [[ -n "$modified_md_files" ]]; then
        # Quick validation of only modified markdown files
        lychee_output=$(env RUST_LOG= lychee \
            --config "$config_file" \
            --format markdown \
            $modified_md_files 2>&1) || lychee_exit=$?

        # Check if lychee found errors (exit code 2)
        if [[ "${lychee_exit:-0}" -eq 2 ]]; then
            # Extract error count from output
            error_count=$(echo "$lychee_output" | grep -oE '🚫 [0-9]+' | awk '{print $2}' || echo "unknown")

            # Block stop and feed reason to Claude
            cat <<EOF
{
  "decision": "block",
  "reason": "Link validation found $error_count broken link(s) in files modified this session:\n\n$lychee_output\n\n⚠️  Please fix broken links before stopping.\n\n💡 Tip: Review full results in $full_results",
  "systemMessage": "⚠️  Lychee: $error_count broken link(s) in modified files"
}
EOF
            exit 0
        fi
    fi
fi

# =============================================================================
# No Errors or Blocking Not Needed - Allow Stop
# =============================================================================

{
    echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ✅ Hook completed - Allowing session stop"
    echo "=========================================================================="
    echo ""
} >> "$log_file" 2>&1

# Log hook completed event
"$HOME/.claude/automation/lychee/runtime/lib/event_logger.py" \
    "$CORRELATION_ID" \
    "$workspace_hash" \
    "$session_id" \
    "hook" \
    "hook.completed" \
    "{}" \
    2>> "$log_file" || {
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ❌ Failed to log hook.completed event" >> "$log_file" 2>&1
        exit 1
    }

exit 0
