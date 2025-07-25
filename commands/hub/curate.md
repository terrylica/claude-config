---
description: Organize and curate tested commands into your collection
argument-hint: "[command-file] [category]"
allowed-tools: Bash, Read, Write
---

# Curate Command: $ARGUMENTS

Managing your curated command collection...

## 🎯 Curation Setup

```bash
args=($ARGUMENTS)
command_file="${args[0]}"
target_category="${args[1]}"

echo "🗂️ Claude Code Command Curation"
echo "==============================="
echo "📅 Date: $(date)"
echo ""

if [ -z "$command_file" ]; then
    echo "Interactive curation mode - browse and organize your commands"
else
    echo "📄 Command: $command_file"
    echo "📁 Target category: ${target_category:-auto-detect}"
fi
```

## 📊 Current Collection Status

```bash
echo "📈 Current Curated Collection:"
echo "============================="

curated_path="$HOME/claude-code-command-hub/curated"
total_curated=0

for category in "$curated_path"/*; do
    if [ -d "$category" ]; then
        cat_name=$(basename "$category")
        count=$(find "$category" -name "*.md" 2>/dev/null | wc -l)
        total_curated=$((total_curated + count))
        
        printf "  %-15s %3d commands\n" "$cat_name:" "$count"
    fi
done

echo "  ────────────────────────────"
printf "  %-15s %3d commands\n" "Total:" "$total_curated"
echo ""
```

## 🔍 Command Processing

```bash
if [ -n "$command_file" ]; then
    # Process specific command file
    echo "🔍 Processing Command File:"
    echo "=========================="
    
    # Resolve full path
    if [[ "$command_file" == /* ]]; then
        full_path="$command_file"
    elif [ -f "$command_file" ]; then
        full_path="$(realpath "$command_file")"
    elif [ -f "$HOME/claude-code-command-hub/repositories/$command_file" ]; then
        full_path="$HOME/claude-code-command-hub/repositories/$command_file"
    elif [ -f "$HOME/claude-code-command-hub/testing/sandbox-*/\\.claude/commands/$(basename "$command_file")" ]; then
        # Find in test environments
        full_path=$(find "$HOME/claude-code-command-hub/testing" -name "$(basename "$command_file")" -path "*/.claude/commands/*" | head -1)
    else
        echo "❌ Command file not found: $command_file"
        echo ""
        echo "🔍 Searching for similar files..."
        filename=$(basename "$command_file")
        find ~/claude-code-command-hub -name "*$filename*" -name "*.md" 2>/dev/null | head -5 | while read -r found; do
            rel_path=${found#$HOME/claude-code-command-hub/}
            echo "  📄 $rel_path"
        done
        exit 1
    fi
    
    if [ ! -f "$full_path" ]; then
        echo "❌ File not accessible: $full_path"
        exit 1
    fi
    
    command_name=$(basename "$full_path" .md)
    echo "✅ Found: $full_path"
    echo "📝 Command: /$command_name"
    
    # Analyze command content for category suggestion
    if [ -z "$target_category" ]; then
        echo ""
        echo "🤖 Auto-detecting category..."
        
        content=$(cat "$full_path")
        
        # Category detection logic
        if echo "$content" | grep -qi "doc\|session\|progress\|log"; then
            suggested_category="docs"
        elif echo "$content" | grep -qi "dev\|code\|review\|build\|test"; then
            suggested_category="dev"  
        elif echo "$content" | grep -qi "project\|task\|manage"; then
            suggested_category="project"
        elif echo "$content" | grep -qi "context\|compact\|memory"; then
            suggested_category="context"
        else
            suggested_category="personal"
        fi
        
        echo "💡 Suggested category: $suggested_category"
        target_category="$suggested_category"
    fi
    
    # Copy to curated collection
    target_dir="$curated_path/$target_category"
    mkdir -p "$target_dir"
    
    target_file="$target_dir/$command_name.md"
    
    if [ -f "$target_file" ]; then
        echo ""
        echo "⚠️  Command already exists in curated collection"
        echo "📄 Existing: $target_file"
        echo "🔄 This will overwrite the existing version"
    fi
    
    cp "$full_path" "$target_file"
    echo "✅ Command curated successfully!"
    echo "📁 Location: $target_file"
    
else
    # Interactive browsing mode
    echo "🔍 Interactive Curation Mode:"
    echo "============================"
    echo ""
    echo "📂 Available sources to curate from:"
    echo ""
    
    # Show test results
    test_results="$HOME/claude-code-command-hub/testing"
    if [ -d "$test_results" ]; then
        tested_count=$(find "$test_results" -name "*.md" -path "*/.claude/commands/*" 2>/dev/null | wc -l)
        echo "  🧪 Tested commands: $tested_count"
        if [ "$tested_count" -gt 0 ]; then
            echo "    Recent tests:"
            find "$test_results" -name "*.md" -path "*/.claude/commands/*" -mtime -7 2>/dev/null | head -3 | while read -r test_cmd; do
                cmd_name=$(basename "$test_cmd" .md)
                test_dir=$(echo "$test_cmd" | sed 's|.*/testing/||' | sed 's|/.*||')
                echo "      - /$cmd_name (from $test_dir)"
            done
        fi
    fi
    
    # Show repositories
    echo ""
    echo "  📚 Repository commands:"
    find "$HOME/claude-code-command-hub/repositories" -name "*.md" \( -path "*/commands/*" -o -path "*/.claude/commands/*" \) 2>/dev/null | wc -l | xargs -I {} echo "    {} total available"
    
    echo ""
    echo "💡 Curation workflow:"
    echo "  1. Test commands: /hub:test <command-file>"
    echo "  2. Curate good ones: /hub:curate <command-file> [category]"
    echo "  3. Deploy to projects: /hub:deploy <project> <category>"
    echo ""
    echo "🎯 Example:"
    echo "  /hub:curate Claude-Command-Suite/commands/dev/code-review.md dev"
fi
```

## 📋 Curation Guidelines

```bash
echo ""
echo "📋 Curation Best Practices:"
echo "=========================="
echo ""
echo "✅ Commands worth curating:"
echo "  - Tested and working correctly"
echo "  - Useful for your workflow"
echo "  - Well-documented with clear descriptions"
echo "  - Safe to run (no dangerous operations)"
echo ""
echo "📁 Category guidelines:"
echo "  - docs: Documentation, session management, logging"
echo "  - dev: Code analysis, development tools, testing"
echo "  - project: Project management, task organization"
echo "  - context: Context management, memory tools"
echo "  - personal: Your custom commands and modifications"
echo ""
echo "🔄 Maintenance:"
echo "  - Review curated commands periodically"
echo "  - Update commands when source repositories change"
echo "  - Remove commands that become obsolete"
```

## 📊 Collection Analysis

```bash
if [ "$total_curated" -gt 0 ]; then
    echo ""
    echo "📈 Collection Analysis:"
    echo "======================"
    
    # Find most recent additions
    echo "🆕 Recent additions (last 7 days):"
    recent_count=$(find "$curated_path" -name "*.md" -mtime -7 2>/dev/null | wc -l)
    if [ "$recent_count" -gt 0 ]; then
        find "$curated_path" -name "*.md" -mtime -7 2>/dev/null | while read -r recent_cmd; do
            cmd_name=$(basename "$recent_cmd" .md)
            category=$(basename "$(dirname "$recent_cmd")")
            echo "  - /$category:$cmd_name"
        done
    else
        echo "  No commands added in the last 7 days"
    fi
    
    # Suggest actions
    echo ""
    echo "💡 Suggestions:"
    if [ "$total_curated" -lt 5 ]; then
        echo "  🎯 Build your collection: Use /hub:discover and /hub:test"
    elif [ "$total_curated" -lt 15 ]; then
        echo "  📈 Growing nicely: Consider /hub:deploy to start using commands"
    else
        echo "  🎉 Mature collection: Regularly /hub:deploy to projects"
    fi
    
    # Check for deployment opportunities
    echo "  🚀 Ready for deployment to projects"
fi
```

## ⏭️ Next Steps

```bash
echo ""
echo "⏭️ Next Steps:"
echo "=============="
echo ""
echo "After curation:"
echo "  1. 🎯 Deploy to projects: /hub:deploy <project-path> <category>"
echo "  2. 🔄 Keep collection updated: /hub:sync and re-curate as needed"
echo "  3. 📊 Monitor usage: /hub:stats"
echo ""
echo "Ongoing curation:"
echo "  - Test new commands: /hub:test <command-file>"
echo "  - Browse updates: /hub:discover"
echo "  - Organize collection: Review categories periodically"
echo ""
echo "📚 Hub commands available:"
echo "  /hub:stats    - View collection statistics"
echo "  /hub:deploy   - Deploy commands to projects"
echo "  /hub:sync     - Update community repositories"
echo "  /hub:discover - Browse available commands"
```

---

**Curation complete!** Your command collection is organized and ready for deployment to projects.