---
description: GitHub Flavored Markdown link integrity checker with intelligent auto-fix
argument-hint: "[workspace-path] [--format|-f text|json] [--no-external|-ne] [--no-completeness|-nc] [--output|-o filename] [--include-ignored|-ii] [--verbose|-v] [--fix|-x]"
allowed-tools: Bash, Task
---

# GFM Link Checker: $ARGUMENTS

**Flags:**
- `--format|-f text|json` - Output format (default: text)
- `--no-external|-ne` - Skip external URL checking (faster)
- `--no-completeness|-nc` - Skip README completeness checking
- `--output|-o filename` - Write report to file instead of stdout
- `--include-ignored|-ii` - Include ignored directories (third-party dependencies, dev environment)
- `--verbose|-v` - Show skipped directories and permission issues
- `--fix|-x` - Auto-fix broken internal links only (external links are reported for manual review)

**Examples:**
- `/gfm-check -x` - Check and auto-fix current directory
- `/gfm-check /docs -ne -x` - Check docs, skip external URLs, auto-fix
- `/gfm-check -f json` - Generate JSON report
- `/gfm-check -o report.txt` - Save report to file
- `/gfm-check -v` - Verbose output showing skipped directories
- `/gfm-check -ii -v` - Include ignored directories with verbose output

**Claude Code Agent Validation:**
- Automatically validates `.claude/agents/` directory compliance
- Checks required frontmatter fields (especially `name:` field)
- Detects non-agent files in agents directory
- Validates agent directory purity (no subdirectories, only `.md` files)

**Direct Usage (from any workspace):**
```
$HOME/.claude/tools/gfm-link-checker/bin/gfm-check [options]
```

```bash
# Parse arguments and preserve working directory
args=($ARGUMENTS)

# Determine workspace path while preserving user's working directory
if [[ -n "${args[0]}" ]]; then
    # User provided explicit path argument
    if [[ "${args[0]}" = /* ]]; then
        # Already absolute path
        workspace_path="${args[0]}"
    else
        # Convert relative path to absolute using user's current working directory
        workspace_path="$(cd "${PWD}/${args[0]}" 2>/dev/null && pwd || echo "${PWD}/${args[0]}")"
    fi
else
    # No path argument - use user's current working directory
    workspace_path="${PWD}"
fi

# Build command arguments and check for --fix flag
cmd_args="$workspace_path"
auto_fix=false
format_next=false

for arg in "${args[@]:1}"; do
    case "$arg" in
        --fix|-x)
            auto_fix=true
            # Don't pass --fix to Python script
            ;;
        --no-external|-ne)
            cmd_args="$cmd_args --no-external"
            ;;
        --no-completeness|-nc)
            cmd_args="$cmd_args --no-completeness"
            ;;
        --include-ignored|-ii)
            cmd_args="$cmd_args --include-ignored"
            ;;
        --verbose|-v)
            cmd_args="$cmd_args --verbose"
            ;;
        --format|-f)
            cmd_args="$cmd_args --format"
            format_next=true
            ;;
        text|json)
            if [[ "$format_next" == "true" ]]; then
                cmd_args="$cmd_args $arg"
                format_next=false
            else
                # Standalone text/json not following --format, ignore
                echo "⚠️  Warning: '$arg' should follow --format/-f flag"
            fi
            ;;
        --output|-o)
            # Pass through --output and expect next arg to be the filename
            cmd_args="$cmd_args $arg"
            ;;
        *)
            # Pass through other valid arguments (like output filenames)
            if [[ "$arg" != --* ]]; then
                cmd_args="$cmd_args $arg"
            else
                echo "⚠️  Warning: Unknown flag '$arg' - ignoring"
            fi
            ;;
    esac
done

# UV Environment Setup and Enforcement
echo "🔧 Ensuring UV-ready environment..."

# Function to check UV availability and setup
check_and_setup_uv() {
    # Check if uv is available
    if ! command -v uv &> /dev/null; then
        echo "❌ UV not found! Python tooling in Claude Code requires UV."
        echo ""
        echo "📦 Install UV:"
        echo "  macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh"
        echo "  Windows:     powershell -c \"irm https://astral.sh/uv/install.sh | iex\""
        echo "  Homebrew:    brew install uv"
        echo ""
        echo "🔄 After installation, restart your terminal and run this command again."
        echo ""
        echo "💡 Why UV? Modern Python dependency management with:"
        echo "   • Fast dependency resolution"
        echo "   • Automatic virtual environment management"
        echo "   • Lock file generation for reproducible builds"
        echo "   • Zero-configuration project setup"
        return 1
    fi
    
    # Check if target workspace has Python project structure
    original_dir=$(pwd)
    cd "$workspace_path" 2>/dev/null || { echo "❌ Cannot access workspace: $workspace_path"; return 1; }
    
    # Look for Python project indicators
    has_pyproject=false
    has_python_files=false
    
    [[ -f "pyproject.toml" ]] && has_pyproject=true
    [[ $(find . -maxdepth 2 -name "*.py" | head -1) ]] && has_python_files=true
    
    if [[ "$has_python_files" == "true" && "$has_pyproject" == "false" ]]; then
        echo "🐍 Python files detected but no pyproject.toml found."
        echo "💡 Consider initializing UV project structure:"
        echo "   cd $workspace_path"
        echo "   uv init --python 3.11"
        echo "   uv add requests  # Example: add dependencies"
        echo ""
        echo "📚 UV commands you'll need:"
        echo "   uv run python script.py    # Run Python scripts"
        echo "   uv add package-name        # Add dependencies"
        echo "   uv sync                    # Install dependencies"
        echo ""
        
        # Offer auto-setup for clean directories
        python_count=$(find "$workspace_path" -maxdepth 2 -name "*.py" | wc -l)
        if [[ $python_count -le 3 ]]; then
            echo "🚀 AUTO-SETUP AVAILABLE: This appears to be a small/new Python project."
            echo "   Run: uv init --python 3.11 && uv add httpx requests"
            echo "   This will create a modern UV-managed Python project."
            echo ""
        fi
    elif [[ "$has_python_files" == "false" && "$has_pyproject" == "false" ]]; then
        # Completely new workspace
        echo "📁 New workspace detected. For Python development:"
        echo "   uv init --python 3.11  # Initialize new Python project"
        echo "   uv add httpx requests   # Add common dependencies"
        echo ""
    fi
    
    # Check for CLAUDE.md and suggest UV preferences
    if [[ ! -f "$workspace_path/.claude/CLAUDE.md" ]]; then
        echo "📝 Consider creating .claude/CLAUDE.md with UV preferences:"
        echo "   mkdir -p .claude"
        echo "   echo '# Python Package Management' >> .claude/CLAUDE.md"
        echo "   echo '- **Primary Tool**: \`uv\` for all Python operations' >> .claude/CLAUDE.md"
        echo "   echo '- **Avoid**: pip, conda, pipenv' >> .claude/CLAUDE.md"
        echo ""
    fi
    
    # Educational UV best practices
    echo "✅ UV environment validated. Key benefits you're now using:"
    echo "   • 10-100x faster dependency resolution than pip"
    echo "   • Automatic virtual environment isolation"
    echo "   • Reproducible builds with uv.lock"
    echo "   • Single tool for project management (no more virtualenv/pip confusion)"
    echo ""
    
    cd "$original_dir"
    return 0
}

# Perform UV check and setup
if ! check_and_setup_uv; then
    echo "❌ Cannot proceed without UV. Please install UV and try again."
    exit 1
fi

# Run the GFM link checker using universal Claude Code path (preserves working directory)  
echo "🔍 Running GFM link integrity check..."
uv run --directory "$HOME/.claude/tools/gfm-link-checker" "$HOME/.claude/tools/gfm-link-checker/gfm_link_checker.py" $cmd_args

# Check exit code and auto-fix if requested
exit_code=$?
if [[ $exit_code -ne 0 && "$auto_fix" == "true" ]]; then
    echo ""
    echo "❌ Link issues found. Initiating intelligent auto-fix process..."
    
    # Re-run with JSON output to get structured error data for analysis
    echo "🔧 Generating structured error report for analysis..."
    json_output=$(uv run --directory "$HOME/.claude/tools/gfm-link-checker" "$HOME/.claude/tools/gfm-link-checker/gfm_link_checker.py" $cmd_args --format json 2>/dev/null)
    
    # Save JSON output to temporary file for agent analysis
    temp_file="/tmp/gfm_check_errors_$(date +%s).json"
    echo "$json_output" > "$temp_file"
    
    echo "📋 Link errors saved to: $temp_file"
    echo "🤖 Deploying specialized link repair agent with deep analysis..."
    echo ""
    echo "🧠 CLAUDE_TASK_REQUEST: Use the Task tool with general-purpose agent to perform comprehensive link repair analysis and fixes."
    echo ""
    echo "📄 ERROR_DATA_FILE: $temp_file"
    echo "📁 TARGET_WORKSPACE: $workspace_path"
    echo ""
    echo "🎯 REPAIR_OBJECTIVES:"
    echo "1. Read and analyze the JSON error report with deep thinking"
    echo "2. Use TodoWrite to create systematic fix plan for all error types"
    echo "3. Implement fixes for FILE_NOT_FOUND, MISSING_README, and ANCHOR_NOT_FOUND errors"
    echo "4. Search workspace intelligently for alternative file locations and correct extensions"
    echo "5. Create missing README.md files where directories are referenced"
    echo "6. Fix GitHub Flavored Markdown anchor references according to official rules"
    echo "7. Re-run GFM checker to verify all fixes are successful"
    echo "8. Report completion status with fixed link counts"
    echo ""
    echo "⚡ AGENT_ACTIVATION_TRIGGER: The above constitutes a request for automated link repair using specialized agent deployment."
fi
```