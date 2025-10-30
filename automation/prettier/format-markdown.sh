#!/usr/bin/env bash
# Prettier Markdown Formatting Stop Hook
# Formats all .md files in workspace when Claude stops responding
# Auto-commits with AI-generated messages using Claude Code headless mode
# Uses fire-and-forget pattern for async execution (< 10ms exit)

set -euo pipefail

# Get workspace directory from Claude Code environment
workspace_dir="${CLAUDE_WORKSPACE_DIR:-$(pwd)}"

# Fire-and-forget async formatting + AI auto-commit - exit immediately
{
    # Step 1: Run mdformat formatting on workspace files (includes table alignment)
    find "$workspace_dir" -type f -name "*.md" \
        -not -path "*/node_modules/*" \
        -not -path "*/.git/*" \
        -not -path "*/file-history/*" \
        -not -path "*/plugins/*" \
        -exec "$HOME/.local/bin/mdformat" \
            --wrap keep \
            {} + 2>/dev/null

    # Step 1b: Also format markdown files in /tmp (no git operations for these)
    # Use /private/tmp on macOS since /tmp is a symlink
    find /private/tmp -maxdepth 3 -type f -name "*.md" \
        -exec "$HOME/.local/bin/mdformat" \
            --wrap keep \
            {} + 2>/dev/null

    # Step 2: Check if mdformat made any changes
    cd "$workspace_dir" 2>/dev/null || exit 0

    # Only proceed if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        exit 0
    fi

    # Check for modified markdown files
    if git diff --quiet '*.md' 2>/dev/null; then
        # No changes - exit silently
        exit 0
    fi

    # Step 3: Stage mdformat changes
    git add '*.md' 2>/dev/null || exit 0

    # Count and list changed files
    changed_files=$(git diff --cached --name-only '*.md' 2>/dev/null | wc -l | tr -d ' ')

    if [[ "$changed_files" -eq 0 ]]; then
        exit 0
    fi

    # Get concise diff summary (first 50 lines to avoid token limits)
    diff_summary=$(git diff --cached --stat '*.md' 2>/dev/null | head -50)
    file_list=$(git diff --cached --name-only '*.md' 2>/dev/null)

    # Step 4: Generate AI commit message using Claude Code headless mode (Haiku - cheapest model)
    commit_prompt="DISABLE_INTERLEAVED_THINKING

Generate a git commit message for these mdformat formatting changes.

Files changed: $changed_files
$file_list

Diff summary:
$diff_summary

CRITICAL: Output ONLY the raw commit message text. Do NOT include:
- No introductory text like 'Here is the commit message:'
- No code blocks or backticks
- No explanations or commentary
- Just the commit message itself

Format:
Line 1: <type>: <summary> (50 chars max)
Line 2: (blank)
Line 3+: optional body (72 chars per line)

Use type: chore, docs, or style

Example output (copy this format exactly):
style: format markdown files with mdformat

Standardized formatting for $changed_files file(s)."

    # Invoke Claude Code in headless mode using Haiku (cheapest model at $1/$5 per MTok)
    # --model haiku: 3x cheaper than Sonnet, 15x cheaper than Opus
    # DISABLE_INTERLEAVED_THINKING: prevents extended thinking tokens
    commit_message=$(timeout 30 claude -p "$commit_prompt" \
        --model claude-haiku-4-5-20251001 \
        --output-format text \
        --allowedTools "Read" 2>/dev/null | \
        # Clean up output: remove common preambles and code blocks
        grep -v -E '^(Here|Based on|The commit|```|$)' | \
        head -10 || echo "")

    # Fallback to default message if Claude fails or returns empty
    if [[ -z "$commit_message" ]] || [[ ${#commit_message} -lt 10 ]]; then
        commit_message="chore: auto-format markdown with mdformat

Automated formatting of $changed_files markdown file(s) by mdformat Stop hook.
Reduces git diff clutter and maintains consistent formatting."
    fi

    # Step 5: Commit with AI-generated or fallback message
    git commit -m "$commit_message" 2>/dev/null || true

} > /dev/null 2>&1 &

# Exit immediately - don't wait for background process
exit 0
