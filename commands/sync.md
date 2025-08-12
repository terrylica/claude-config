---
description: Universal cross-platform Claude Code workspace synchronization with canonical session architecture - seamless development across macOS and Ubuntu environments
argument-hint: "[--status|--sync-sessions|--push-workspace|--pull-workspace|--all] [--dry-run] [--verbose] [--force] [--migrate-sessions]"
allowed-tools: Task, Bash, Read
---

# Universal Cross-Platform Workspace Sync: $ARGUMENTS

**Revolutionary Claude Code workspace and session synchronization with canonical session architecture**
**Enables seamless session resumption across macOS ↔ Ubuntu environments**

**Flags:**
- `--status` - Check sync infrastructure health and model availability
- `--sync-sessions` - Universal cross-platform session sync with canonical format
- `--migrate-sessions` - Migrate platform-specific sessions to canonical format
- `--push-workspace` - Push local workspace to remote
- `--pull-workspace` - Pull remote workspace to local
- `--all` - Execute comprehensive sync (push workspace + canonical sessions + status)
- `--dry-run` - Preview changes without executing
- `--verbose` - Detailed output and diagnostics
- `--force` - Skip confirmations and force operations

**Examples:**
- `/sync --status --verbose` - Comprehensive health check with canonical session validation
- `/sync --sync-sessions` - Universal cross-platform session sync with automatic migration
- `/sync --migrate-sessions --dry-run` - Preview canonical session migration without changes
- `/sync --all --dry-run` - Preview complete cross-platform sync operation
- `/sync --push-workspace --sync-sessions` - Full development environment sync
- `/sync --force --sync-sessions` - Force canonical session sync (resolves path conflicts)

```bash
# Parse arguments
args=($ARGUMENTS)
operation=""
dry_run_flag=""
verbose_flag=""
force_flag=""

# Default to status if no arguments
if [[ ${#args[@]} -eq 0 ]]; then
    operation="--status --verbose"
else
    # Parse all arguments
    for arg in "${args[@]}"; do
        case "$arg" in
            --status|--sync-sessions|--migrate-sessions|--push-workspace|--pull-workspace|--all)
                operation="$operation $arg"
                ;;
            --dry-run)
                dry_run_flag="--dry-run"
                ;;
            --verbose)
                verbose_flag="--verbose"
                ;;
            --force)
                force_flag="--force"
                ;;
        esac
    done
    
    # Default to status if no operation specified
    if [[ -z "$operation" ]]; then
        operation="--status --verbose"
    fi
fi

# Build final command
sync_command="$HOME/.claude/sage-aliases/bin/sage-sync $operation $dry_run_flag $verbose_flag $force_flag"

echo "🔄 CLAUDE CODE WORKSPACE SYNC"
echo "============================="
echo "📋 Operation: $operation"
echo "🔧 Options: $dry_run_flag $verbose_flag $force_flag"
echo "📡 Target: GPU Workstation (tca)"
echo ""

echo "🤖 AGENT_DEPLOYMENT: Using Task tool with 'workspace-sync' agent for universal canonical session management."
echo ""
echo "🎯 UNIVERSAL SYNC OBJECTIVES:"
echo "1. Environment Validation & Cross-Platform Connectivity"
echo "   • SSH connection to GPU workstation (tca host)"
echo "   • ZeroTier network status and fallback routing"
echo "   • Local and remote workspace integrity verification"
echo "   • Cross-platform path compatibility assessment"
echo ""
echo "2. Canonical Session Architecture Execution"
echo "   • Execute: $sync_command"
echo "   • Universal cross-platform session synchronization"
echo "   • Automatic migration of platform-specific sessions to canonical format"
echo "   • Intelligent session deduplication with UUID-based merging"
echo ""
echo "3. SAGE Models & Infrastructure Status"
echo "   • Local/remote model availability (alphaforge, nautilus_trader, etc.)"
echo "   • Python package consistency (pycatch22, tsfresh)"
echo "   • TiRex GPU availability and CUDA status"
echo "   • Cross-platform development environment verification"
echo ""
echo "4. Revolutionary Claude Sessions Management"
echo "   • Universal canonical session format (~eon-nt, ~scripts, ~-claude)"
echo "   • Cross-platform session consolidation (macOS + Ubuntu → Universal)"
echo "   • Seamless session resumption across any platform"
echo "   • Workspace-relative path mapping for true portability"
echo ""
echo "5. Universal Cross-Platform Validation & Recommendations"
echo "   • Canonical session format verification and integrity checks"
echo "   • Cross-platform session availability validation"
echo "   • Universal workspace compatibility assessment"
echo "   • Performance metrics for canonical session architecture"
echo ""
echo "💡 REVOLUTIONARY WORKFLOW INTEGRATION:"
echo "   • Initial setup: /sync --migrate-sessions (convert existing sessions)"
echo "   • Before switching to GPU: /sync --push-workspace --sync-sessions"
echo "   • Before switching to local: /sync --pull-workspace --sync-sessions"
echo "   • Regular cross-platform sync: /sync --all --verbose"
echo "   • Emergency session recovery: /sync --sync-sessions --force"
echo "   • Session migration preview: /sync --migrate-sessions --dry-run"
echo ""
echo "🚀 CANONICAL SESSION BENEFITS:"
echo "   • Resume any session from any platform (macOS ↔ Ubuntu)"
echo "   • Universal workspace compatibility (~eon-nt works everywhere)"
echo "   • Automatic platform-specific session consolidation"
echo "   • Zero manual path translation or configuration required"
echo ""

# Success indicator for automation
echo "✅ SYNC_COMMAND_READY: $sync_command"
```