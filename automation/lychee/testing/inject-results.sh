#!/usr/bin/env bash
# Lychee SessionStart Hook - Result Injection
# Version: 0.1.0
# Spec: ~/.claude/specifications/lychee-link-validation.yaml
#
# Purpose: Inject previous session validation results as context
# Execution: On SessionStart event
# Output: Markdown-formatted results to stdout (becomes Claude context)

set -euo pipefail

# =============================================================================
# Configuration
# =============================================================================

full_results="/tmp/claude_lychee_full.txt"

# =============================================================================
# Check if Results Exist
# =============================================================================

# Only inject if results file exists and is non-empty
if [[ ! -s "$full_results" ]]; then
    exit 0
fi

# =============================================================================
# Check for Errors
# =============================================================================

# Look for error indicator in results (🚫 followed by non-zero number)
if ! grep -q '🚫.*[1-9]' "$full_results" 2>/dev/null; then
    # No errors - optionally show success message
    # Uncomment below to always show validation status:
    # echo ""
    # echo "✅ All links validated successfully in previous session"
    # echo ""
    exit 0
fi

# =============================================================================
# Inject Results with Errors
# =============================================================================

cat <<EOF

📊 **Link Validation Results** (previous session)

$(tail -15 "$full_results")

⚠️  Broken links detected. Would you like me to help fix them?

EOF

exit 0
