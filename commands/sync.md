---
description: Comprehensive Claude Code workspace synchronization with GPU workstation - intelligent sync operations for dual-environment development
argument-hint: "[--status|--sync-sessions|--push-workspace|--pull-workspace|--all] [--dry-run] [--verbose] [--force]"
allowed-tools: Task, Bash, Read
---

# Workspace Sync: $ARGUMENTS

**Comprehensive Claude Code workspace and session synchronization with remote GPU workstation**

**Flags:**
- `--status` - Check sync infrastructure health and model availability
- `--sync-sessions` - Sync Claude sessions to GPU workstation
- `--push-workspace` - Push local workspace to remote
- `--pull-workspace` - Pull remote workspace to local
- `--all` - Execute comprehensive sync (push workspace + sessions + status)
- `--dry-run` - Preview changes without executing
- `--verbose` - Detailed output and diagnostics
- `--force` - Skip confirmations and force operations

**Examples:**
- `/sync --status --verbose` - Comprehensive health check
- `/sync --sync-sessions` - Sync Claude sessions only
- `/sync --all --dry-run` - Preview full sync operation
- `/sync --push-workspace --force` - Force push workspace changes

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
            --status|--sync-sessions|--push-workspace|--pull-workspace|--all)
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

echo "🤖 AGENT_DEPLOYMENT: Using Task tool with 'general-purpose' agent for comprehensive sync management."
echo ""
echo "🎯 SYNC_OBJECTIVES:"
echo "1. Environment Validation & Connectivity Check"
echo "   • SSH connection to GPU workstation (tca host)"
echo "   • ZeroTier network status and fallback routing"
echo "   • Local and remote workspace integrity verification"
echo "   • Disk space and resource availability assessment"
echo ""
echo "2. Sync Operation Execution"
echo "   • Execute: $sync_command"
echo "   • Intelligent incremental sync with rsync compression"
echo "   • Git integration with automatic backup creation"
echo "   • Comprehensive progress monitoring and error handling"
echo ""
echo "3. SAGE Models & Infrastructure Status"
echo "   • Local/remote model availability (alphaforge, nautilus_trader, etc.)"
echo "   • Python package consistency (pycatch22, tsfresh)"
echo "   • TiRex GPU availability and CUDA status"
echo "   • Cross-platform compatibility verification"
echo ""
echo "4. Claude Sessions Management"
echo "   • Bidirectional session synchronization (~/.claude/system/sessions/)"
echo "   • Session conflict detection and resolution"
echo "   • Conversation history preservation across environments"
echo "   • Working directory context maintenance"
echo ""
echo "5. Post-Sync Validation & Recommendations"
echo "   • Sync completion verification and file count validation"
echo "   • Performance metrics and transfer efficiency analysis"
echo "   • Next-step recommendations for development workflow"
echo "   • Maintenance suggestions and optimization opportunities"
echo ""
echo "💡 WORKFLOW_INTEGRATION:"
echo "   • Before switching to GPU: /sync --push-workspace --sync-sessions"
echo "   • Before switching to local: /sync --pull-workspace"
echo "   • Regular health check: /sync --status --verbose"
echo "   • Emergency sync: /sync --sync-sessions --force"
echo ""

# Success indicator for automation
echo "✅ SYNC_COMMAND_READY: $sync_command"
```