---
description: "Validate command-agent pair alignment and auto-suggestion completeness"
argument-hint: "[command-name] | --create [new-command] | --fix [command] | --list | --validate-all"
allowed-tools: Task, Bash, Read, Glob, Grep, Write, Edit, LS
---

# Command-Agent Alignment Checker

**Purpose**: Validate and ensure proper alignment between command files and their corresponding agent specifications, with focus on auto-suggestion completeness and argument hint accuracy.

**Usage Options**:
- `/command-agent-check [command-name]` - Validate specific command-agent pair
- `/command-agent-check --create [new-command]` - Create new command-agent pair from scratch
- `/command-agent-check --fix [command]` - Auto-fix alignment issues in existing command
- `/command-agent-check --list` - List all commands and their agent alignment status
- `/command-agent-check --validate-all` - Validate all command-agent pairs in workspace

## Validation Framework

**Alignment Checks**:
1. **Frontmatter Completeness**
   - `description` field presence and clarity
   - `argument-hint` field with option coverage
   - `allowed-tools` alignment with agent capabilities
   - Optional fields (`model`, `temperature`) consistency

2. **Agent Correspondence**
   - Matching agent file exists in `~/.claude/agents/`
   - Agent capabilities match command options
   - Usage patterns alignment between command and agent
   - Tool access consistency

3. **Auto-Suggestion Optimization**
   - Argument hint shows all available options/flags
   - Option syntax follows Claude Code conventions
   - Help text clarity for user guidance
   - Parameter format consistency

4. **Functional Validation**
   - Command invocation patterns work correctly
   - Agent deployment instructions are accurate
   - Error handling and edge case coverage
   - Documentation synchronization

```bash
# Parse arguments and set mode
args=($ARGUMENTS)
command_name="${args[0]}"
mode="validate"

# Determine operation mode
case "$command_name" in
    --create)
        mode="create"
        target_name="${args[1]}"
        ;;
    --fix)
        mode="fix"
        target_name="${args[1]}"
        ;;
    --list)
        mode="list"
        ;;
    --validate-all)
        mode="validate-all"
        ;;
    *)
        mode="validate"
        target_name="$command_name"
        ;;
esac

echo "🔍 Command-Agent Alignment Checker"
echo "=================================="
echo "Mode: $mode"
[[ -n "$target_name" ]] && echo "Target: $target_name"
echo ""

# =============================================================================
# LIST MODE - Show all commands and agent alignment status
# =============================================================================
if [[ "$mode" == "list" ]]; then
    echo "📋 Command-Agent Alignment Status"
    echo "================================="
    
    commands_dir="$HOME/.claude/commands"
    agents_dir="$HOME/.claude/agents"
    
    if [[ -d "$commands_dir" ]]; then
        for cmd_file in "$commands_dir"/*.md; do
            [[ ! -f "$cmd_file" ]] && continue
            
            cmd_basename=$(basename "$cmd_file" .md)
            agent_file="$agents_dir/${cmd_basename}.md"
            
            # Check frontmatter
            has_description=$(grep -q "^description:" "$cmd_file" && echo "✓" || echo "○")
            has_arg_hint=$(grep -q "^argument-hint:" "$cmd_file" && echo "✓" || echo "○")
            has_agent=$([ -f "$agent_file" ] && echo "✓" || echo "○")
            
            echo "📄 $cmd_basename"
            echo "   Description: $has_description | Arg-Hint: $has_arg_hint | Agent: $has_agent"
        done
    else
        echo "❌ Commands directory not found: $commands_dir"
    fi
    
    echo ""
    echo "Legend: ✓ = Present | ○ = Missing"
    exit 0
fi

# =============================================================================
# CREATE MODE - Create new command-agent pair
# =============================================================================
if [[ "$mode" == "create" ]]; then
    if [[ -z "$target_name" ]]; then
        echo "❌ Error: Please specify command name to create"
        echo "Usage: /command-agent-check --create [new-command-name]"
        exit 1
    fi
    
    echo "🚀 Creating Command-Agent Pair: $target_name"
    echo "============================================"
    
    command_file="$HOME/.claude/commands/${target_name}.md"
    agent_file="$HOME/.claude/agents/${target_name}.md"
    
    # Check if files already exist
    if [[ -f "$command_file" ]] || [[ -f "$agent_file" ]]; then
        echo "⚠️  Warning: Files already exist!"
        [[ -f "$command_file" ]] && echo "   Command: $command_file"
        [[ -f "$agent_file" ]] && echo "   Agent: $agent_file"
        echo ""
        echo "Use --fix mode to update existing files instead."
        exit 1
    fi
    
    # Interactive creation process
    echo "📝 Command Template Creation Process"
    echo "Please provide the following information:"
    echo ""
    echo "AGENT_TASK_REQUEST: Use Task tool with 'simple-helper' agent for interactive command-agent pair creation."
    echo ""
    echo "🎯 CREATION_PARAMETERS:"
    echo "   COMMAND_NAME: $target_name"
    echo "   COMMAND_FILE: $command_file"
    echo "   AGENT_FILE: $agent_file"
    echo "   MODE: interactive_creation"
    echo ""
    echo "📋 REQUIRED_INPUTS:"
    echo "1. Command purpose and description"
    echo "2. Available options and argument patterns"
    echo "3. Agent capabilities and tool requirements"
    echo "4. Usage examples and patterns"
    echo "5. Integration requirements"
    echo ""
    exit 0
fi

# =============================================================================
# VALIDATE MODE - Check specific command-agent pair
# =============================================================================
if [[ "$mode" == "validate" ]] || [[ "$mode" == "validate-all" ]]; then
    
    validate_command_agent_pair() {
        local cmd_name="$1"
        local cmd_file="$HOME/.claude/commands/${cmd_name}.md"
        local agent_file="$HOME/.claude/agents/${cmd_name}.md"
        
        echo "🔍 Validating: $cmd_name"
        echo "========================"
        
        # 1. File Existence Check
        local cmd_exists="false"
        local agent_exists="false"
        
        if [[ -f "$cmd_file" ]]; then
            cmd_exists="true"
            echo "✅ Command file: $cmd_file"
        else
            echo "❌ Command file missing: $cmd_file"
        fi
        
        if [[ -f "$agent_file" ]]; then
            agent_exists="true"
            echo "✅ Agent file: $agent_file"
        else
            echo "⚠️  Agent file missing: $agent_file (optional)"
        fi
        
        # 2. Frontmatter Validation
        if [[ "$cmd_exists" == "true" ]]; then
            echo ""
            echo "📋 Frontmatter Analysis"
            echo "----------------------"
            
            # Check required fields
            if grep -q "^description:" "$cmd_file"; then
                description=$(grep "^description:" "$cmd_file" | cut -d'"' -f2)
                echo "✅ Description: \"$description\""
            else
                echo "❌ Missing description field"
            fi
            
            if grep -q "^argument-hint:" "$cmd_file"; then
                arg_hint=$(grep "^argument-hint:" "$cmd_file" | sed 's/^argument-hint: //')
                echo "✅ Argument hint: $arg_hint"
                
                # Analyze argument complexity
                option_count=$(echo "$arg_hint" | grep -o '\--[a-zA-Z-]*\|[|\[]' | wc -l)
                if [[ $option_count -gt 3 ]]; then
                    echo "✅ Rich option coverage ($option_count options/patterns)"
                else
                    echo "⚠️  Simple options ($option_count patterns) - consider expanding"
                fi
            else
                echo "❌ Missing argument-hint field"
            fi
            
            # Check optional fields
            if grep -q "^allowed-tools:" "$cmd_file"; then
                tools=$(grep "^allowed-tools:" "$cmd_file" | sed 's/^allowed-tools: //')
                echo "✅ Allowed tools: $tools"
            else
                echo "ℹ️  No tool restrictions specified"
            fi
        fi
        
        # 3. Agent Alignment Check
        if [[ "$cmd_exists" == "true" ]] && [[ "$agent_exists" == "true" ]]; then
            echo ""
            echo "🤝 Command-Agent Alignment"
            echo "-------------------------"
            
            # Extract usage patterns from both files
            cmd_usage_count=$(grep -c "Usage\|usage" "$cmd_file" || echo "0")
            agent_usage_count=$(grep -c "Usage\|usage" "$agent_file" || echo "0")
            
            if [[ $cmd_usage_count -gt 0 ]] && [[ $agent_usage_count -gt 0 ]]; then
                echo "✅ Both files contain usage documentation"
            else
                echo "⚠️  Usage documentation incomplete"
                echo "   Command usage patterns: $cmd_usage_count"
                echo "   Agent usage patterns: $agent_usage_count"
            fi
            
            # Check for tool consistency
            if grep -q "allowed-tools:" "$cmd_file" && grep -q "Tools:" "$agent_file"; then
                echo "✅ Tool specifications present in both files"
            else
                echo "ℹ️  Tool specifications may need alignment review"
            fi
        fi
        
        # 4. Auto-Suggestion Readiness Score
        echo ""
        echo "📊 Auto-Suggestion Readiness Score"
        echo "---------------------------------"
        
        local score=0
        local max_score=10
        
        # Scoring criteria
        [[ -f "$cmd_file" ]] && ((score++))
        [[ -f "$cmd_file" ]] && grep -q "^description:" "$cmd_file" && ((score++))
        [[ -f "$cmd_file" ]] && grep -q "^argument-hint:" "$cmd_file" && ((score++))
        [[ -f "$cmd_file" ]] && grep -q "Usage Options\|usage options" "$cmd_file" && ((score++))
        [[ -f "$cmd_file" ]] && [[ $(wc -l < "$cmd_file") -gt 20 ]] && ((score++))
        [[ -f "$agent_file" ]] && ((score++))
        [[ -f "$cmd_file" ]] && [[ $(grep -o '\--[a-zA-Z-]*' "$cmd_file" | wc -l) -gt 2 ]] && ((score++))
        [[ -f "$cmd_file" ]] && grep -q "allowed-tools:" "$cmd_file" && ((score++))
        [[ -f "$cmd_file" ]] && grep -q "Examples:\|examples:" "$cmd_file" && ((score++))
        [[ -f "$cmd_file" ]] && [[ -f "$agent_file" ]] && ((score++))
        
        local percentage=$((score * 100 / max_score))
        echo "Score: $score/$max_score ($percentage%)"
        
        if [[ $percentage -ge 80 ]]; then
            echo "✅ Excellent auto-suggestion readiness"
        elif [[ $percentage -ge 60 ]]; then
            echo "⚠️  Good readiness - minor improvements possible"
        else
            echo "❌ Poor readiness - significant improvements needed"
        fi
        
        echo ""
        echo "=" # Separator for multiple validations
        echo ""
    }
    
    if [[ "$mode" == "validate-all" ]]; then
        echo "🔍 Validating All Command-Agent Pairs"
        echo "====================================="
        echo ""
        
        commands_dir="$HOME/.claude/commands"
        if [[ -d "$commands_dir" ]]; then
            for cmd_file in "$commands_dir"/*.md; do
                [[ ! -f "$cmd_file" ]] && continue
                cmd_basename=$(basename "$cmd_file" .md)
                validate_command_agent_pair "$cmd_basename"
            done
        else
            echo "❌ Commands directory not found: $commands_dir"
        fi
    else
        if [[ -z "$target_name" ]]; then
            echo "❌ Error: Please specify command name to validate"
            echo "Usage: /command-agent-check [command-name]"
            exit 1
        fi
        
        validate_command_agent_pair "$target_name"
    fi
fi

# =============================================================================
# FIX MODE - Auto-repair command-agent alignment issues
# =============================================================================
if [[ "$mode" == "fix" ]]; then
    if [[ -z "$target_name" ]]; then
        echo "❌ Error: Please specify command name to fix"
        echo "Usage: /command-agent-check --fix [command-name]"
        exit 1
    fi
    
    echo "🔧 Auto-Fix Mode: $target_name"
    echo "==============================="
    
    echo "AGENT_TASK_REQUEST: Use Task tool with 'simple-helper' agent for command-agent alignment repair."
    echo ""
    echo "🎯 FIX_PARAMETERS:"
    echo "   COMMAND_NAME: $target_name"
    echo "   COMMAND_FILE: ~/.claude/commands/${target_name}.md"
    echo "   AGENT_FILE: ~/.claude/agents/${target_name}.md"
    echo "   MODE: auto_repair"
    echo ""
    echo "🔧 FIX_OBJECTIVES:"
    echo "1. Add missing frontmatter fields (description, argument-hint)"
    echo "2. Enhance argument-hint with comprehensive option coverage"
    echo "3. Align command options with agent capabilities"
    echo "4. Improve auto-suggestion readiness score"
    echo "5. Standardize documentation format"
    echo ""
fi

echo "💡 Quick Commands:"
echo "• List all: /command-agent-check --list"
echo "• Validate all: /command-agent-check --validate-all"
echo "• Create new: /command-agent-check --create [name]"
echo "• Fix existing: /command-agent-check --fix [name]"
echo ""
echo "## Claude Code Agent Color Reference"
echo ""
echo "### Available Color Options (12 total):"
echo ""
echo "Primary Colors (Confirmed Working):"
echo "• red - Critical operations, auditing, compliance"
echo "• blue - Research, analysis, information gathering"  
echo "• green - Development, building, success operations"
echo "• yellow - Warnings, monitoring, status checks"
echo "• purple - Quality assurance, testing, validation"
echo "• orange - Refactoring, housekeeping, maintenance"
echo "• cyan - Synchronization, networking, connectivity"
echo "• pink - Creative tasks, documentation, user-facing"
echo "• gray - Utility, helper, basic operations"
echo ""
echo "Standard Colors (Terminal-dependent):"
echo "• black - System-level operations"
echo "• white - Output formatting, reports"
echo "• magenta - Specialized tasks"
echo ""
echo "### Color Format Requirements:"
echo "• YAML Syntax: 'color: red' (lowercase, no quotes needed)"
echo "• Location: Must be in YAML frontmatter section"
echo "• Case: Use lowercase for consistency"
echo "• Unsupported: Hex codes (#ff0000), RGB values, complex names"
```