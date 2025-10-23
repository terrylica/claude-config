---
description: Claude Code session synchronization using verified ~/.claude/projects/ standard - automatic bidirectional sync across macOS and Linux environments
argument-hint: "[--status|--sync-sessions|--migrate-sessions] [--dry-run] [--verbose] [--force]"
allowed-tools: Task, Bash, Read
---

# Claude Session Sync: $ARGUMENTS

**🎯 PURPOSE: Claude Code session synchronization using Docker-verified official standard**
**🔄 SCOPE: Sessions only - use Git for workspace synchronization**
**🖥️ AUTOMATIC BIDIRECTIONAL: Auto-detects macOS ↔ Linux and syncs both directions in one command**

## Recommended Workflow

### 1. 📁 Workspace Sync (Use Git)

```bash
# Push changes to remote repository
git add . && git commit -m "Work in progress" && git push

# Pull latest changes on other system
git pull
```

### 2. 🗂️ Session Sync (Use sage-sync)

```bash
# Automatically sync Claude sessions in both directions (local → remote, remote → local)
/sync --sync-sessions --verbose
```

### 3. ✅ Status Check

```bash
# Verify sync infrastructure health
/sync --status
```

## Available Actions

- `--sync-sessions` - Automatically sync Claude sessions bidirectionally using official ~/.claude/projects/ format
- `--migrate-sessions` - Migrate sessions from legacy format to official standard
- `--status` - Check sync infrastructure health and model availability

## Options

- `--dry-run` - Preview changes without executing
- `--verbose` - Detailed output and diagnostics
- `--force` - Skip confirmations and force operations
- `--version` - Show version and system configuration

## Examples

- `/sync --sync-sessions --verbose` - Bidirectionally sync sessions with detailed logging
- `/sync --migrate-sessions --dry-run` - Preview legacy session migration
- `/sync --status` - Check system health and connectivity
- `/sync --version` - Show bidirectional configuration

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
echo "2. Automatic Bidirectional Session Sync Execution"
echo "   • Execute: $sync_command"
echo "   • Step 1: Push local sessions to remote (local → remote)"
echo "   • Step 2: Pull remote sessions to local (remote → local)"
echo "   • Cross-platform session synchronization using ~/.claude/projects/"
echo "   • Docker-verified official Claude Code format with --update safety"
echo ""
echo "3. SAGE Models & Infrastructure Status"
echo "   • Local/remote model availability (alphaforge, nautilus_trader, etc.)"
echo "   • Python package consistency (pycatch22, tsfresh)"
echo "   • TiRex GPU availability and CUDA status"
echo "   • Cross-platform development environment verification"
echo ""
echo "4. Official Claude Sessions Management"
echo "   • Official ~/.claude/projects/ format (Docker-verified)"
echo "   • Cross-platform session sync (macOS ↔ Ubuntu)"
echo "   • Seamless session resumption using native Claude behavior"
echo "   • Path-encoded directory names for workspace identification"
echo ""
echo "5. Cross-Platform Validation & Recommendations"
echo "   • Official session format verification and integrity checks"
echo "   • Cross-platform session availability validation"
echo "   • Native Claude Code compatibility assessment"
echo "   • Performance metrics for official session architecture"
echo ""
echo "💡 OFFICIAL WORKFLOW INTEGRATION:"
echo "   • Initial setup: /sync --migrate-sessions (convert to official format)"
echo "   • Before switching to GPU: /sync --push-workspace --sync-sessions"
echo "   • Before switching to local: /sync --pull-workspace --sync-sessions"
echo "   • Regular cross-platform sync: /sync --all --verbose"
echo "   • Emergency session recovery: /sync --sync-sessions --force"
echo "   • Session migration preview: /sync --migrate-sessions --dry-run"
echo ""
echo "🚀 OFFICIAL SESSION BENEFITS:"
echo "   • Resume sessions from any platform (macOS ↔ Ubuntu)"
echo "   • Native Claude Code compatibility (Docker-verified)"
echo "   • Simple path-encoded directory structure"
echo "   • No custom transformations or complexity required"
echo ""

# Success indicator for automation
echo "✅ SYNC_COMMAND_READY: $sync_command"
```
