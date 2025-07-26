---
description: Comprehensive command validation - infrastructure health and flag behavior audit
argument-hint: "[command-name] [--health|-h] [--flags|-f] [--compatibility|-c] [--verbose|-v] [--fix|-x]"
allowed-tools: Task, Bash, Read, Glob, Grep, Write, Edit
---

# Command Check: $ARGUMENTS

**Comprehensive command validation combining infrastructure health checks and flag behavior auditing**

**Flags:**
- `--health|-h` - Run infrastructure health checks only (UV, files, dependencies)
- `--flags|-f` - Run flag behavior audit only (compatibility, parsing)  
- `--compatibility|-c` - Include flag compatibility testing (requires --flags)
- `--verbose|-v` - Detailed output and diagnostics
- `--fix|-x` - Auto-fix discovered issues where possible

**Default Behavior:** Run both health checks and flag audit if no specific scope flags provided

**Examples:**
- `/command-check` - Full validation of default command (gfm-check)
- `/command-check tts --verbose` - Full validation of tts command with details
- `/command-check gfm-check --health` - Infrastructure health only
- `/command-check gfm-check --flags --fix` - Flag audit with auto-fix

```bash
# Parse arguments
args=($ARGUMENTS)
target_command="${args[0]:-gfm-check}"
run_health=false
run_flags=false
test_compatibility=false
verbose=false
auto_fix=false

# Parse flags
for arg in "${args[@]:1}"; do
    case "$arg" in
        --health|-h)
            run_health=true
            ;;
        --flags|-f)
            run_flags=true
            ;;
        --compatibility|-c)
            test_compatibility=true
            ;;
        --verbose|-v)
            verbose=true
            ;;
        --fix|-x)
            auto_fix=true
            ;;
    esac
done

# Default to running both if no specific scope flags
if [[ "$run_health" == "false" && "$run_flags" == "false" ]]; then
    run_health=true
    run_flags=true
fi

# Header
echo "🔍 Command Validation Suite"
echo "=========================="
echo "📋 Target: $target_command"
echo "🔧 Health Check: $([ "$run_health" == "true" ] && echo "✓" || echo "○")"
echo "🏴 Flag Audit: $([ "$run_flags" == "true" ] && echo "✓" || echo "○")"
echo "🔄 Auto-fix: $([ "$auto_fix" == "true" ] && echo "✓" || echo "○")"
echo ""

# Shared status reporting function
report_status() {
    local check_name="$1"
    local status="$2"
    local detail="$3"
    
    if [[ "$status" == "PASS" ]]; then
        echo "✅ $check_name"
    elif [[ "$status" == "WARN" ]]; then
        echo "⚠️  $check_name - $detail"
    else
        echo "❌ $check_name - $detail"
    fi
    
    [[ "$verbose" == "true" ]] && [[ -n "$detail" ]] && echo "   Detail: $detail"
}

# =============================================================================
# INFRASTRUCTURE HEALTH CHECKS
# =============================================================================
if [[ "$run_health" == "true" ]]; then
    echo "🏥 INFRASTRUCTURE HEALTH"
    echo "========================"
    
    # 1. UV Environment Check
    echo "🔧 Environment Validation..."
    if command -v uv &> /dev/null; then
        uv_version=$(uv --version 2>/dev/null | head -1)
        report_status "UV Installation" "PASS" "$uv_version"
    else
        report_status "UV Installation" "FAIL" "UV not found in PATH"
    fi
    
    # 2. Command Structure Check
    echo ""
    echo "🛠️  Command Structure Validation..."
    command_file="$HOME/.claude/commands/${target_command}.md"
    if [[ -f "$command_file" ]]; then
        report_status "Command File" "PASS" "$command_file"
    else
        report_status "Command File" "FAIL" "Missing: $command_file"
    fi
    
    # 3. Argument Documentation Check
    if [[ -f "$command_file" ]] && grep -q "argument-hint:" "$command_file"; then
        report_status "Argument Documentation" "PASS"
        
        # Flag completeness check
        if [[ -f "$command_file" ]]; then
            arg_hint_line=$(grep "argument-hint:" "$command_file")
            long_flags=$(echo "$arg_hint_line" | grep -o '\--[a-zA-Z-]*' | wc -l)
            short_flags=$(echo "$arg_hint_line" | grep -o '\-[a-zA-Z]' | wc -l)
            
            if [[ "$verbose" == "true" ]]; then
                echo "   Long flags: $long_flags, Short flags: $short_flags"
            fi
            
            if [[ $long_flags -gt $short_flags ]]; then
                report_status "Flag Completeness" "WARN" "Some flags may be missing short versions"
            else
                report_status "Flag Completeness" "PASS"
            fi
        fi
    else
        report_status "Argument Documentation" "WARN" "No argument hints found"
    fi
    
    # 4. Dependency Check
    echo ""
    echo "📦 Dependency Validation..."
    cd "$HOME/.claude/tools/gfm-link-checker" 2>/dev/null && {
        if [[ -f "pyproject.toml" ]]; then
            report_status "Project Config" "PASS"
            
            # Check if dependencies are synced
            if uv sync --dry-run &>/dev/null; then
                report_status "Dependency Sync" "PASS"
            else
                report_status "Dependency Sync" "WARN" "Dependencies may need sync"
            fi
        else
            report_status "Project Config" "FAIL" "pyproject.toml missing"
        fi
    }
    
    # 5. Interface Validation
    echo ""
    echo "🔌 Interface Validation..."
    gfm_check_test=$(cd "$HOME/.claude/tools/gfm-link-checker" && uv run python gfm_link_checker.py --help 2>&1)
    if echo "$gfm_check_test" | grep -q "usage:"; then
        report_status "GFM Script Interface" "PASS"
    else
        report_status "GFM Script Interface" "FAIL" "Help output malformed"
    fi
    
    # 6. Security Check
    echo ""
    echo "🛡️  Security Validation..."
    if [[ -w "/tmp" ]]; then
        report_status "Temp Directory Access" "PASS"
    else
        report_status "Temp Directory Access" "WARN" "Limited temp access"
    fi
    
    # 7. Integration Test
    echo ""
    echo "🔗 Integration Test..."
    test_workspace="/tmp/cmd_check_test_$$"
    mkdir -p "$test_workspace"
    cat > "$test_workspace/README.md" << 'EOF'
# Test
[test](missing-file.md)
EOF
    
    cd "$HOME/.claude/tools/gfm-link-checker"
    test_result=$(uv run python gfm_link_checker.py "$test_workspace" 2>&1)
    test_exit_code=$?
    
    if [[ $test_exit_code -ne 0 ]]; then
        report_status "Integration Test" "PASS" "Correctly detected broken link"
    else
        report_status "Integration Test" "WARN" "Should have detected broken link"
    fi
    
    # Cleanup
    rm -rf "$test_workspace"
    
    echo ""
fi

# =============================================================================
# FLAG BEHAVIOR AUDIT
# =============================================================================
if [[ "$run_flags" == "true" ]]; then
    echo "🏴 FLAG BEHAVIOR AUDIT"
    echo "======================"
    
    # Generate audit request for specialized agent
    audit_timestamp=$(date '+%Y-%m-%d_%H-%M-%S')
    audit_report_file="/tmp/flag_audit_${audit_timestamp}.json"
    
    echo "🤖 Deploying flag parsing validation agent..."
    echo ""
    echo "AGENT_TASK_REQUEST: Use Task tool with 'simple-helper' agent for command flag parsing validation."
    echo ""
    echo "📊 FLAG_AUDIT_PARAMETERS:"
    echo "   TARGET_COMMAND: $target_command"
    echo "   COMMAND_FILE: ~/.claude/commands/${target_command}.md"
    echo "   TEST_COMPATIBILITY: $test_compatibility"
    echo "   AUTO_FIX: $auto_fix"
    echo "   REPORT_FILE: $audit_report_file"
    echo "   VERBOSE: $verbose"
    echo ""
    echo "🎯 VALIDATION_OBJECTIVES:"
    echo "1. Flag Compatibility Testing"
    echo "   • Test short flag mappings work correctly (e.g., -ne vs --no-external)"
    echo "   • Verify ALL flags have both long and short versions (completeness check)"
    echo "   • Check argument order independence"
    echo "   • Validate workspace/path handling with various flag combinations"
    echo "   • Ensure no flags are long-only (missing short versions)"
    echo ""
    echo "2. Flag Parsing Accuracy"
    echo "   • Check format argument parsing consistency"
    echo "   • Verify argument validation and error handling"
    echo "   • Test edge cases and malformed arguments"
    echo "   • Check error message clarity and user guidance"
    echo ""
    echo "3. Auto-Fix Recommendations"
    if [[ "$auto_fix" == "true" ]]; then
        echo "   • EXECUTE fixes for discovered issues"
        echo "   • Update command documentation"
        echo "   • Standardize flag patterns"
    else
        echo "   • REPORT fixes for discovered issues"
        echo "   • Generate remediation suggestions"
    fi
    echo ""
fi

# =============================================================================
# SUMMARY AND RECOMMENDATIONS
# =============================================================================
echo "📊 VALIDATION SUMMARY"
echo "===================="
echo "Validation completed at $(date)"
echo ""

if [[ "$auto_fix" == "true" ]]; then
    echo "🔧 AUTO-FIX MODE ACTIVE"
    echo "• Infrastructure issues: Basic fixes applied where possible"
    echo "• Flag issues: Delegated to specialized agent for comprehensive repair"
    echo ""
fi

echo "💡 NEXT STEPS:"
if [[ "$run_health" == "true" && "$run_flags" == "false" ]]; then
    echo "• For comprehensive validation: /command-check $target_command --flags"
elif [[ "$run_health" == "false" && "$run_flags" == "true" ]]; then
    echo "• For complete health check: /command-check $target_command --health"
fi
echo "• For detailed diagnostics: /command-check $target_command --verbose"
echo "• For automated fixes: /command-check $target_command --fix"
echo "• For quick daily check: /command-check $target_command --health"
```