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

# Cleanup stale hook processes to prevent file caching issues
source "$HOME/.claude/automation/lib/cleanup-stale-hooks.sh" && cleanup_stale_hooks 2>/dev/null || true

# Suppress uv debug output (prevents "Stop hook error" in Claude Code CLI)
export UV_NO_PROGRESS=1
export RUST_LOG=error

# =============================================================================
# Configuration
# =============================================================================

config_file="$HOME/.claude/.lycheerc.toml"
log_file="$HOME/.claude/automation/lychee/logs/lychee.log"
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
# Get current working directory (where Claude CLI is running)
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

# Detect git repository root (where .git lives)
# cd to workspace_dir first to ensure git commands work correctly
cd "$workspace_dir" || exit 1
git_root=$(git rev-parse --show-toplevel 2>/dev/null || echo "$workspace_dir")

# Calculate relative path from git root to current directory
if [[ "$workspace_dir" == "$git_root" ]]; then
    relative_dir="."
else
    relative_dir="${workspace_dir#$git_root/}"
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

# Extract last assistant and user messages from transcript for Session Summary
last_assistant_message=""
last_user_prompt=""

# Extract transcript_path from hook input (Claude CLI provides this)
if [[ -n "$hook_input" ]]; then
    transcript_file=$(echo "$hook_input" | jq -r '.transcript_path // ""' 2>/dev/null)
else
    transcript_file=""
fi

if [[ -n "$transcript_file" && -f "$transcript_file" ]]; then
    {
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] 📝 Found transcript: $transcript_file"
        echo "   → File size: $(ls -lh "$transcript_file" 2>/dev/null | awk '{print $5}' || echo 'unknown')"
        echo "   → Line count: $(wc -l < "$transcript_file" 2>/dev/null || echo 'unknown')"
    } >> "$log_file"

    # Extract last assistant message (text block content)
    # JSONL format: each line is a wrapper object with nested message
    # Structure: {message: {role: "assistant", content: [...]}}

    {
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] 🔍 DEBUG: Starting assistant message extraction..."
        echo "   → Using tail -50 + tac (file size: $(ls -lh "$transcript_file" 2>/dev/null | awk '{print $5}' || echo 'unknown'))"
    } >> "$log_file"

    # Use tail -50 + tac instead of full-file tac for better performance
    # Research: 28.6% faster, 99.95% less I/O (reads ~10KB vs 21MB)
    # 50 lines sufficient for typical conversation endings
    tac_output=$(tail -50 "$transcript_file" | tac 2>&1) || {
        tac_exit=$?
        {
            echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ❌ DEBUG: tail+tac command failed!"
            echo "   → Exit code: $tac_exit"
            echo "   → Error output: ${tac_output:0:500}"
        } >> "$log_file"
        last_assistant_message=""
    }

    if [[ -n "${tac_output:-}" ]]; then
        {
            echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ✅ DEBUG: tac completed successfully"
            echo "   → Output length: ${#tac_output} bytes"
            echo "   → Starting jq parsing..."
        } >> "$log_file"

        # Parse with jq
        last_assistant_message=$(echo "$tac_output" | \
            jq -r '.message | select(.role == "assistant") | .content[] | select(.type == "text") | .text' 2>&1 | \
            head -1 | \
            head -c 200) || {
            jq_exit=$?
            {
                echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ❌ DEBUG: jq command failed!"
                echo "   → Exit code: $jq_exit"
            } >> "$log_file"
            last_assistant_message=""
        }

        {
            echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ✅ DEBUG: jq parsing completed"
            echo "   → Extracted message length: ${#last_assistant_message} chars"
        } >> "$log_file"
    fi

    # Extract first line only (often a summary or heading)
    if [[ -n "$last_assistant_message" ]]; then
        last_assistant_message=$(echo "$last_assistant_message" | head -1 | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ✅ Extracted last response: ${last_assistant_message:0:80}..." >> "$log_file"
    else
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ⚠️  No assistant text content found in transcript" >> "$log_file"
    fi

    # Extract last user prompt (the question that triggered the response)
    # Skip tool_result messages (content is array) and system messages (content starts with <)
    # Only extract actual user text prompts (content is string)

    {
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] 🔍 DEBUG: Starting user prompt extraction..."
        echo "   → Using tail -500 for performance (reads ~100KB vs 21MB full file)"
    } >> "$log_file"

    # Use tail -500 without tac for reliability
    # Research: tail reads ~100KB vs tac reading 21MB (prevents timeout)
    # 500 lines provides sufficient history for user prompts in long debugging sessions
    # Process forward and use tail -1 to get most recent matching message
    tac_output_user=$(tail -500 "$transcript_file" 2>&1) || {
        tac_exit=$?
        {
            echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ❌ DEBUG: tail command (user prompt) failed!"
            echo "   → Exit code: $tac_exit"
        } >> "$log_file"
        last_user_prompt=""
    }

    if [[ -n "${tac_output_user:-}" ]]; then
        {
            echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ✅ DEBUG: tac (user prompt) completed"
            echo "   → Starting jq + grep pipeline..."
        } >> "$log_file"

        # Extract last user prompt (handles both string and array content formats)
        # Array format: {"content": [{"type": "text", "text": "message"}]}
        # String format: {"content": "message"}  (legacy)
        # Note: Skip Telegram notification echoes (multi-line blocks starting with ``` and ending with ```)
        last_user_prompt=$(echo "$tac_output_user" | \
            jq -r '
                # Get first user message with actual text content (not tool_result)
                first(
                    select(.message.role == "user") |
                    select(if (.message.content | type) == "array" then
                        # Must have text content and no tool_result
                        ([.message.content[] | select(.type == "text")] | length > 0) and
                        ([.message.content[] | select(.type == "tool_result")] | length == 0)
                    else
                        # String content must not be empty
                        .message.content != ""
                    end)
                ) |
                # Extract text content
                if (.message.content | type) == "string" then
                    .message.content
                elif (.message.content | type) == "array" then
                    ([.message.content[] | select(.type == "text") | .text] | join("\n"))
                else
                    empty
                end' | \
            sed '/^```$/,/^```$/d' | \
            grep -v "^$" | grep -v "^<" | grep -v "^Caveat:" | grep -v '^\`\`\`' | \
            awk 'NF {print; exit}' | \
            head -c 500) || {
            {
                echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ❌ DEBUG: User prompt pipeline failed!"
            } >> "$log_file"
            last_user_prompt=""
        }

        {
            echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ✅ DEBUG: User prompt extraction completed"
            echo "   → Extracted prompt length: ${#last_user_prompt} chars"
        } >> "$log_file"
    fi

    # Clean up user prompt (preserve multi-line, trim whitespace)
    if [[ -n "$last_user_prompt" ]]; then
        last_user_prompt=$(echo "$last_user_prompt" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        prompt_preview=$(echo "$last_user_prompt" | head -c 60 | tr '\n' '␤')
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ✅ Extracted user prompt: ${prompt_preview}..." >> "$log_file"
    else
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ⚠️  No user prompt found in transcript" >> "$log_file"
    fi
else
    if [[ -n "$transcript_file" ]]; then
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ⚠️  Transcript not found: $transcript_file" >> "$log_file"
    else
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ⚠️  No transcript_path in hook input" >> "$log_file"
    fi
fi

# Fallback to workspace name if no message extracted
if [[ -z "$last_assistant_message" ]]; then
    last_assistant_message="Session completed"
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

# =============================================================================
# Extract Git Status (Phase 2 - v4.0.0)
# =============================================================================

# Change to workspace directory for git commands
cd "$workspace_dir" 2>/dev/null || {
    {
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ⚠️  Failed to cd to workspace: $workspace_dir"
    } >> "$log_file" 2>&1
}

# Extract git information
git_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
modified_files=$(git status --porcelain 2>/dev/null | { grep -E "^( M|M )" || true; } | wc -l | tr -d ' \n')
untracked_files=$(git status --porcelain 2>/dev/null | { grep "^??" || true; } | wc -l | tr -d ' \n')
staged_files=$(git status --porcelain 2>/dev/null | { grep -E "^(M |A |D |R |C )" || true; } | wc -l | tr -d ' \n')

# Get git porcelain output (up to 10 lines) for Telegram display
git_porcelain_raw=$(git status --porcelain 2>/dev/null | head -10 || echo "")
git_porcelain_json=$(echo "$git_porcelain_raw" | jq -R -s 'split("\n") | map(select(length > 0))' 2>/dev/null || echo "[]")

# Get ahead/behind commits (requires remote tracking branch)
ahead_commits=0
behind_commits=0
if git rev-parse --abbrev-ref @{u} >/dev/null 2>&1; then
    ahead_commits=$(git rev-list --count @{u}..HEAD 2>/dev/null | tr -d '\n' || echo "0")
    behind_commits=$(git rev-list --count HEAD..@{u} 2>/dev/null | tr -d '\n' || echo "0")
fi

# Fallback to 0 if any git command failed
git_branch="${git_branch:-unknown}"
modified_files="${modified_files:-0}"
untracked_files="${untracked_files:-0}"
staged_files="${staged_files:-0}"
ahead_commits="${ahead_commits:-0}"
behind_commits="${behind_commits:-0}"

# =============================================================================
# Calculate Session Duration (Phase 2 - v4.0.0)
# =============================================================================

# Read start timestamp from SessionStart hook
TIMESTAMP_DIR="$HOME/.claude/automation/lychee/state/session_timestamps"
timestamp_file="$TIMESTAMP_DIR/${session_id}.timestamp"

if [[ -f "$timestamp_file" ]]; then
    # Read start timestamp
    session_start_time=$(cat "$timestamp_file" 2>/dev/null || echo "0")
    session_end_time=$(date +%s)
    session_duration=$((session_end_time - session_start_time))

    # Clean up timestamp file
    rm -f "$timestamp_file" 2>/dev/null || true

    {
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ⏱️  Session duration: ${session_duration}s (start: $session_start_time, end: $session_end_time)"
    } >> "$log_file" 2>&1
else
    # Fallback: Use 0 if timestamp not found
    session_duration=0
    {
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ⚠️  Session start timestamp not found, duration set to 0"
        echo "   → Expected file: $timestamp_file"
    } >> "$log_file" 2>&1
fi

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
    >> /dev/null 2>> "$log_file" || {
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ❌ Failed to log hook.started event" >> "$log_file" 2>&1
        exit 1
    }

# =============================================================================
# SessionSummary Writer Function (Phase 2 - v4.0.0)
# =============================================================================

write_session_summary() {
    local summary_file="$1"
    local lychee_ran="$2"
    local broken_links_count="$3"
    local results_file_path="$4"

    {
        echo ""
        echo "=========================================================================="
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] 🔍 DEBUG: INSIDE write_session_summary function"
        echo "=========================================================================="
        echo "   → summary_file: $summary_file"
        echo "   → lychee_ran: $lychee_ran"
        echo "   → broken_links_count: $broken_links_count"
        echo "   → results_file_path: $results_file_path"
        echo "   → modified_files: $modified_files"
        echo "   → session_duration: $session_duration"
        echo "   → last_assistant_message length: ${#last_assistant_message}"
        echo "   → last_user_prompt length: ${#last_user_prompt}"
        echo "=========================================================================="
    } >> "$log_file" 2>&1

    # Calculate available workflows using helper script
    local lib_dir="$HOME/.claude/automation/lychee/runtime/lib"
    local state_dir="$HOME/.claude/automation/lychee/state"

    {
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] 🔍 DEBUG: Calling calculate_workflows.py..."
        echo "   → lib_dir: $lib_dir"
        echo "   → state_dir: $state_dir"
    } >> "$log_file" 2>&1

    available_wfs_json=$("$lib_dir/calculate_workflows.py" \
        --error-count "$broken_links_count" \
        --modified-files "$modified_files" \
        --registry "$state_dir/workflows.json" 2>&1) || {
        wf_exit=$?
        {
            echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ❌ DEBUG: calculate_workflows.py FAILED!"
            echo "   → Exit code: $wf_exit"
            echo "   → Output: $available_wfs_json"
        } >> "$log_file" 2>&1
        available_wfs_json="[]"
    }

    {
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ✅ DEBUG: calculate_workflows.py completed"
        echo "   → Result: $available_wfs_json"
    } >> "$log_file" 2>&1

    # Prepare lychee status details
    local lychee_details=""
    if [[ "$broken_links_count" -gt 0 ]]; then
        lychee_details="Found $broken_links_count broken link(s) in workspace"
    else
        lychee_details="No broken links found"
    fi

    # Write SessionSummary JSON
    {
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] 🔍 DEBUG: About to write JSON file..."
        echo "   → Target file: $summary_file"
        echo "   → Target directory: $(dirname "$summary_file")"
        echo "   → Directory exists: $([ -d "$(dirname "$summary_file")" ] && echo 'YES' || echo 'NO')"
        echo "   → Directory writable: $([ -w "$(dirname "$summary_file")" ] && echo 'YES' || echo 'NO')"
    } >> "$log_file" 2>&1

    # Ensure directory exists
    mkdir -p "$(dirname "$summary_file")" 2>> "$log_file" || {
        {
            echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ❌ DEBUG: Failed to create directory!"
            echo "   → Directory: $(dirname "$summary_file")"
        } >> "$log_file" 2>&1
        return 1
    }

    cat > "$summary_file" 2>> "$log_file" <<EOF
{
  "correlation_id": "$CORRELATION_ID",
  "workspace_path": "$workspace_dir",
  "repository_root": "$git_root",
  "working_directory": "$relative_dir",
  "workspace_id": "$workspace_hash",
  "session_id": "$session_id",
  "last_user_prompt": $(echo "$last_user_prompt" | jq -R -s .),
  "last_response": $(echo "$last_assistant_message" | jq -R -s .),
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "duration_seconds": $session_duration,
  "git_status": {
    "branch": "$git_branch",
    "modified_files": $modified_files,
    "untracked_files": $untracked_files,
    "staged_files": $staged_files,
    "ahead_commits": $ahead_commits,
    "behind_commits": $behind_commits,
    "porcelain": $git_porcelain_json
  },
  "lychee_status": {
    "ran": $lychee_ran,
    "error_count": $broken_links_count,
    "details": "$lychee_details",
    "results_file": "$results_file_path"
  },
  "available_workflows": $available_wfs_json
}
EOF

    cat_exit=$?
    {
        if [[ $cat_exit -eq 0 ]]; then
            echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ✅ DEBUG: cat > command succeeded"
        else
            echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ❌ DEBUG: cat > command FAILED!"
            echo "   → Exit code: $cat_exit"
        fi
    } >> "$log_file" 2>&1

    {
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] 📝 SessionSummary written to: $summary_file"
        if [[ -f "$summary_file" ]]; then
            echo "   → ✅ File exists after write"
            echo "   → File size: $(ls -lh "$summary_file" 2>/dev/null | awk '{print $5}' || echo 'unknown')"
            echo "   → Available workflows: $(echo "$available_wfs_json" | jq -r 'length' 2>/dev/null || echo 'unknown')"
        else
            echo "   → ❌ FILE DOES NOT EXIST AFTER WRITE!"
        fi
    } >> "$log_file" 2>&1
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
        >> /dev/null 2>> "$log_file" || true

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
            >> /dev/null 2>> "$log_file" || true

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
    # Set up trap to catch any exits in background job
    trap 'exit_code=$?; { echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ❌ DEBUG: Background job exiting with code $exit_code at line $LINENO"; echo "   → Command: $BASH_COMMAND"; } >> "$log_file" 2>&1' EXIT ERR

    {
        echo ""
        echo "=========================================================================="
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] 🔍 DEBUG: BACKGROUND JOB STARTED"
        echo "=========================================================================="
        echo "   → Background PID: $$"
        echo "   → Parent PID: $PPID"
        echo "   → Workspace: $workspace_dir"
        echo "   → Session ID: $session_id"
        echo "   → set -e is active: $(set -o | grep errexit | awk '{print $2}')"
        echo "   → set -u is active: $(set -o | grep nounset | awk '{print $2}')"
        echo "   → set -o pipefail is active: $(set -o | grep pipefail | awk '{print $2}')"
        echo "=========================================================================="
        echo ""
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
        # Capture exit code to detect crashes
        lychee_exit_code=0
        env RUST_LOG= lychee \
            --config "$config_file" \
            --format markdown \
            $markdown_files \
            > "$full_results" 2>&1 || lychee_exit_code=$?

        # Generate JSON output for programmatic parsing (progressive disclosure)
        json_results="${full_results%.txt}.json"
        env RUST_LOG= lychee \
            --config "$config_file" \
            --format json \
            $markdown_files \
            > "$json_results" 2>&1 || true

        # Log completion with timestamp and summary
        {
            echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ✓ Lychee validation completed (exit code: $lychee_exit_code)"
            echo "   → Results written to: $full_results"
            echo "   → Summary line:"
            tail -1 "$full_results" 2>/dev/null || echo "     (No summary line found)"
        } >> "$log_file" 2>&1

        # =====================================================================
        # Robust Error Detection (handles crashes, malformed output, errors)
        # =====================================================================

        # Extract error count from lychee results (look for "🚫 Errors" line)
        error_count=$(grep '🚫 Errors' "$full_results" | grep -oE '[0-9]+' | head -1 || echo "0")

        # Detect lychee crashes or malformed output (missing summary line)
        has_summary_line=$(grep -c '🚫 Errors\|✅ Successful\|Summary' "$full_results" 2>/dev/null || echo "0")
        has_error_stacktrace=$(grep -c '^Error:\|Stack backtrace:\|\[ERROR\]' "$full_results" 2>/dev/null || echo "0")

        # If lychee crashed (non-zero exit, no summary, has stacktrace), count as 1+ errors
        if [[ $lychee_exit_code -ne 0 ]] || [[ $has_summary_line -eq 0 ]] || [[ $has_error_stacktrace -gt 0 ]]; then
            if [[ $error_count -eq 0 ]]; then
                # Count actual [ERROR] lines or default to 1
                error_lines=$(grep -c '^\[ERROR\]' "$full_results" 2>/dev/null || echo "0")
                if [[ $error_lines -gt 0 ]]; then
                    error_count=$error_lines
                else
                    error_count=1  # At least one error (lychee crash)
                fi

                {
                    echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ⚠️  Lychee crash/malformed output detected!"
                    echo "   → Exit code: $lychee_exit_code"
                    echo "   → Has summary line: $has_summary_line"
                    echo "   → Has error stacktrace: $has_error_stacktrace"
                    echo "   → Detected errors: $error_count"
                } >> "$log_file" 2>&1
            fi
        fi

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

        # =====================================================================
        # Phase 2 - v4.0.0: ALWAYS emit SessionSummary (dual-mode)
        # =====================================================================

        # Emit SessionSummary (v4 format) - ALWAYS, regardless of error count
        {
            echo ""
            echo "=========================================================================="
            echo "[$(date +%Y-%m-%d\ %H:%M:%S)] 📝 DEBUG: About to emit SessionSummary"
            echo "=========================================================================="
            echo "   → Session ID: $session_id"
            echo "   → Workspace hash: $workspace_hash"
            echo "   → Error count: $error_count"
            echo "   → Last assistant message: ${last_assistant_message:0:80}"
            echo "   → Last user prompt: ${last_user_prompt:0:60}"
            echo "   → Full results: $full_results"
            echo "=========================================================================="
            echo ""
            echo "[$(date +%Y-%m-%d\ %H:%M:%S)] 📝 Emitting SessionSummary (v4.0.0)..."
        } >> "$log_file" 2>&1

        summary_file="$HOME/.claude/automation/lychee/state/summaries/summary_${session_id}_${workspace_hash}.json"

        {
            echo "[$(date +%Y-%m-%d\ %H:%M:%S)] 🔍 DEBUG: Calling write_session_summary function..."
            echo "   → Arguments: $summary_file, true, $error_count, $full_results"
        } >> "$log_file" 2>&1

        write_session_summary "$summary_file" "true" "$error_count" "$full_results" 2>> "$log_file" || {
            write_exit=$?
            {
                echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ❌ DEBUG: write_session_summary FAILED!"
                echo "   → Exit code: $write_exit"
            } >> "$log_file" 2>&1
        }

        {
            echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ✅ DEBUG: write_session_summary completed"
            echo "   → Checking if file was created..."
            if [[ -f "$summary_file" ]]; then
                echo "   → ✅ File exists: $summary_file"
                echo "   → File size: $(ls -lh "$summary_file" 2>/dev/null | awk '{print $5}' || echo 'unknown')"
            else
                echo "   → ❌ FILE NOT CREATED: $summary_file"
            fi
        } >> "$log_file" 2>&1

        # Log summary.created event
        "$HOME/.claude/automation/lychee/runtime/lib/event_logger.py" \
            "$CORRELATION_ID" \
            "$workspace_hash" \
            "$session_id" \
            "hook" \
            "summary.created" \
            "{\"error_count\": $error_count, \"summary_file\": \"$summary_file\"}" \
            >> /dev/null 2>> "$log_file" || {
                echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ❌ Failed to log summary.created event" >> "$log_file" 2>&1
            }

        # =====================================================================
        # Phase 2 - v4.0.0: v3 Notification System Removed (v5.5.2)
        # =====================================================================
        # v3 notification system (error-only) was replaced by v4 SessionSummary
        # + workflow menu pattern in Phase 2 v4.0.0. Code was disabled with
        # `if false` and has now been archived.
        #
        # Archive location: automation/lychee/archive/v5.5.0-legacy-notification-system/
        #
        # v4 SessionSummary provides superior UX:
        # - Shows on EVERY session (not just errors)
        # - Multi-workflow support (not just lychee)
        # - More context (git status, session duration, available workflows)

        # =====================================================================
        # Phase 5 - Bot Management: Continuous Process via launchd + watchexec
        # =====================================================================
        # Bot runs continuously as launchd service (production mode)
        # This hook only creates summary files - bot picks them up automatically

        {
            echo ""
            echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ✅ SessionSummary created - bot will pick it up automatically"
            echo "   → Bot managed by launchd service (check status: bot-service.sh status)"
        } >> "$log_file" 2>&1
    else
        # No markdown files found - still emit SessionSummary (v4.0.0)
        {
            echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ⚠️  No markdown files found in $workspace_dir"
            echo "   → Emitting SessionSummary with lychee_ran=false"
        } >> "$log_file" 2>&1

        # Emit SessionSummary even when lychee didn't run
        summary_file="$HOME/.claude/automation/lychee/state/summaries/summary_${session_id}_${workspace_hash}.json"
        write_session_summary "$summary_file" "false" "0" ""

        # Log summary.created event
        "$HOME/.claude/automation/lychee/runtime/lib/event_logger.py" \
            "$CORRELATION_ID" \
            "$workspace_hash" \
            "$session_id" \
            "hook" \
            "summary.created" \
            "{\"error_count\": 0, \"summary_file\": \"$summary_file\", \"lychee_ran\": false}" \
            >> /dev/null 2>> "$log_file" || {
                echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ❌ Failed to log summary.created event" >> "$log_file" 2>&1
            }

        # Bot should be running continuously via watchexec
        # No need to start it here - bot picks up summary files automatically
        {
            echo "   → ✅ SessionSummary created - bot will process it automatically"
        } >> "$log_file" 2>&1
    fi

    {
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] 🏁 TIER 1: Background validation complete"
    } >> "$log_file" 2>&1
} > /dev/null 2>&1 &

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
    >> /dev/null 2>> "$log_file" || {
        echo "[$(date +%Y-%m-%d\ %H:%M:%S)] ❌ Failed to log hook.completed event" >> "$log_file" 2>&1
        exit 1
    }

exit 0
