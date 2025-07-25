---
description: Browse and discover new community commands
allowed-tools: Bash, Read
---

# Discover New Commands

Exploring the Claude Code command ecosystem...

## 🆕 Recent Additions (Last 7 Days)

```bash
cd ~/claude-code-command-hub/repositories

echo "🔍 Commands added in the last 7 days:"

recent_files=$(find . -name "*.md" \( -path "*/commands/*" -o -path "*/.claude/commands/*" \) -mtime -7 2>/dev/null)

if [ -n "$recent_files" ]; then
    echo "$recent_files" | while read -r file; do
        # Extract command name and source
        cmd_name=$(basename "$file" .md)
        source_path=$(dirname "$file" | sed 's|^\./||')
        mod_time=$(stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$file" 2>/dev/null || stat -c "%y" "$file" 2>/dev/null | cut -d' ' -f1,2 | cut -d'.' -f1)
        
        echo "  📄 /$cmd_name"
        echo "     Source: $source_path"
        echo "     Modified: $mod_time"
        
        # Show brief description if available
        if grep -q "description:" "$file" 2>/dev/null; then
            desc=$(grep "description:" "$file" | head -1 | sed 's/description: *//g' | tr -d '"')
            echo "     Description: $desc"
        fi
        echo ""
    done
else
    echo "  No new commands found in the last 7 days"
    echo "  (This is normal if repositories haven't been updated recently)"
fi
```

## 📊 Popular Command Categories

```bash
echo "📈 Command distribution by category:"

cd ~/claude-code-command-hub/repositories

# Analyze command structure
echo ""
echo "By repository source:"
for repo_dir in */; do
    if [ -d "$repo_dir" ]; then
        repo_name=${repo_dir%/}
        cmd_count=$(find "$repo_dir" -name "*.md" \( -path "*/commands/*" -o -path "*/.claude/commands/*" \) 2>/dev/null | wc -l)
        if [ "$cmd_count" -gt 0 ]; then
            printf "  %-25s %3d commands\n" "$repo_name:" "$cmd_count"
        fi
    fi
done

echo ""
echo "By command category (where organized):"

# Look for categorized commands
for category in dev docs project test security deploy context; do
    count=$(find . -name "*.md" -path "*/$category/*" 2>/dev/null | wc -l)
    if [ "$count" -gt 0 ]; then
        printf "  %-15s %3d commands\n" "$category:" "$count"
    fi
done
```

## 🎯 Featured Commands

```bash
echo ""
echo "⭐ Featured commands worth exploring:"

# Look for commonly used patterns
cd ~/claude-code-command-hub/repositories

# Find documentation-related commands
doc_commands=$(find . -name "*.md" \( -path "*/commands/*" -o -path "*/.claude/commands/*" \) -exec grep -l -i "doc\|session\|progress" {} \; 2>/dev/null | head -3)
if [ -n "$doc_commands" ]; then
    echo ""
    echo "📚 Documentation & Session Management:"
    echo "$doc_commands" | while read -r file; do
        cmd_name=$(basename "$file" .md)
        source_repo=$(echo "$file" | cut -d'/' -f2)
        echo "  - /$cmd_name (from $source_repo)"
    done
fi

# Find development commands
dev_commands=$(find . -name "*.md" \( -path "*/commands/*" -o -path "*/.claude/commands/*" \) -exec grep -l -i "code\|review\|test\|build" {} \; 2>/dev/null | head -3)
if [ -n "$dev_commands" ]; then
    echo ""
    echo "⚙️ Development & Code Analysis:"
    echo "$dev_commands" | while read -r file; do
        cmd_name=$(basename "$file" .md)
        source_repo=$(echo "$file" | cut -d'/' -f2)
        echo "  - /$cmd_name (from $source_repo)"
    done
fi

# Find project management commands
project_commands=$(find . -name "*.md" \( -path "*/commands/*" -o -path "*/.claude/commands/*" \) -exec grep -l -i "project\|task\|manage" {} \; 2>/dev/null | head -3)
if [ -n "$project_commands" ]; then
    echo ""
    echo "📋 Project Management:"
    echo "$project_commands" | while read -r file; do
        cmd_name=$(basename "$file" .md)
        source_repo=$(echo "$file" | cut -d'/' -f2)
        echo "  - /$cmd_name (from $source_repo)"
    done
fi
```

## 🔍 Interactive Browse

```bash
echo ""
echo "🗂️ Available repositories to explore:"

cd ~/claude-code-command-hub/repositories

for repo_dir in */; do
    if [ -d "$repo_dir" ]; then
        repo_name=${repo_dir%/}
        cmd_count=$(find "$repo_dir" -name "*.md" \( -path "*/commands/*" -o -path "*/.claude/commands/*" \) 2>/dev/null | wc -l)
        
        if [ "$cmd_count" -gt 0 ]; then
            echo "  📁 $repo_name ($cmd_count commands)"
            
            # Show directory structure if commands are organized
            if [ -d "$repo_dir/commands" ] || [ -d "$repo_dir/.claude/commands" ]; then
                echo "     Structure:"
                find "$repo_dir" -type d -name "commands" -o -name ".claude" | while read -r cmd_dir; do
                    if [ "$cmd_dir" != "$repo_dir.claude" ]; then
                        echo "       $cmd_dir/"
                        find "$cmd_dir" -name "*.md" 2>/dev/null | head -3 | while read -r file; do
                            cmd_name=$(basename "$file" .md)
                            echo "         - $cmd_name"
                        done
                        cmd_total=$(find "$cmd_dir" -name "*.md" 2>/dev/null | wc -l)
                        if [ "$cmd_total" -gt 3 ]; then
                            echo "         ... and $((cmd_total - 3)) more"
                        fi
                    fi
                done
            fi
            echo ""
        fi
    fi
done
```

## 💡 Exploration Tips

```bash
echo "🎯 How to explore further:"
echo ""
echo "📖 Browse specific repository:"
echo "   find ~/claude-code-command-hub/repositories/<repo-name>/ -name '*.md' -path '*/commands/*'"
echo ""
echo "🔍 Search for specific functionality:"
echo "   grep -r -i 'keyword' ~/claude-code-command-hub/repositories/*/commands/ 2>/dev/null"
echo ""
echo "🧪 Test a command safely:"
echo "   /hub:test <repo-name>/commands/<category>/<command>.md"
echo ""
echo "📄 Read command details:"
echo "   cat ~/claude-code-command-hub/repositories/<repo>/<path>/<command>.md"
echo ""
echo "🏷️ Common search keywords:"
echo "   - 'git' for version control commands"  
echo "   - 'doc' for documentation workflows"
echo "   - 'test' for testing automation"
echo "   - 'deploy' for deployment scripts"
echo "   - 'review' for code review tools"
echo ""
echo "📊 View hub statistics:"
echo "   /hub:stats"
```

## 🚀 Quick Actions

```bash
echo ""
echo "⚡ Quick actions you can take now:"
echo ""

# Count interesting commands by type
git_commands=$(find ~/claude-code-command-hub/repositories/ -name "*.md" \( -path "*/commands/*" -o -path "*/.claude/commands/*" \) -exec grep -l -i "git" {} \; 2>/dev/null | wc -l)
doc_commands=$(find ~/claude-code-command-hub/repositories/ -name "*.md" \( -path "*/commands/*" -o -path "*/.claude/commands/*" \) -exec grep -l -i "doc\|session" {} \; 2>/dev/null | wc -l)
test_commands=$(find ~/claude-code-command-hub/repositories/ -name "*.md" \( -path "*/commands/*" -o -path "*/.claude/commands/*" \) -exec grep -l -i "test" {} \; 2>/dev/null | wc -l)

echo "  📊 Found $git_commands git-related commands"
echo "  📚 Found $doc_commands documentation commands"  
echo "  🧪 Found $test_commands testing commands"
echo ""
echo "  💡 Try: /hub:test to safely evaluate any command"
echo "  🎯 Try: /hub:curate to organize your favorites"
echo "  🚀 Try: /hub:deploy to add commands to projects"
```

---

**Discovery complete!** Use `/hub:test <command-file>` to safely try any command you found interesting.