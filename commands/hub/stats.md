---
description: Show Claude Code Command Hub statistics and overview
allowed-tools: Bash, Read
---

# Claude Code Command Hub Statistics

## 📊 Hub Overview

```bash
echo "🎯 Claude Code Command Hub Statistics"
echo "====================================="
echo "📅 Generated: $(date)"
echo ""

cd ~/claude-code-command-hub

# Basic directory stats
echo "📂 Hub Structure:"
echo "  📁 Location: ~/claude-code-command-hub/"
echo "  💾 Disk Usage: $(du -sh . 2>/dev/null | cut -f1)"
echo ""
```

## 🏛️ Repository Statistics

```bash
echo "📚 Repository Statistics:"
echo "========================"

cd repositories

repo_count=0
total_commands=0
active_repos=0

for repo_dir in */; do
    if [ -d "$repo_dir" ]; then
        repo_count=$((repo_count + 1))
        repo_name=${repo_dir%/}
        
        # Count commands in this repo
        cmd_count=$(find "$repo_dir" -name "*.md" \( -path "*/commands/*" -o -path "*/.claude/commands/*" \) 2>/dev/null | wc -l)
        
        if [ "$cmd_count" -gt 0 ]; then
            active_repos=$((active_repos + 1))
            total_commands=$((total_commands + cmd_count))
            
            # Get last update
            if [ -d "$repo_dir/.git" ]; then
                last_update=$(cd "$repo_dir" && git log -1 --format="%ad" --date=short 2>/dev/null || echo "Unknown")
                printf "  %-25s %3d commands (updated: %s)\n" "$repo_name:" "$cmd_count" "$last_update"
            else
                printf "  %-25s %3d commands (no git info)\n" "$repo_name:" "$cmd_count"
            fi
        else
            printf "  %-25s %3d commands (inactive)\n" "$repo_name:" "$cmd_count"
        fi
    fi
done

echo ""
echo "📈 Repository Summary:"
echo "  📁 Total repositories: $repo_count"
echo "  ✅ Active repositories: $active_repos"
echo "  📄 Total commands: $total_commands"
```

## 🎯 Curated Collection Statistics

```bash
echo ""
echo "🗂️ Curated Collection:"
echo "======================"

cd ~/claude-code-command-hub/curated

curated_total=0
echo "  📋 Commands by category:"

for category in */; do
    if [ -d "$category" ]; then
        cat_name=${category%/}
        cmd_count=$(find "$category" -name "*.md" 2>/dev/null | wc -l)
        curated_total=$((curated_total + cmd_count))
        
        if [ "$cmd_count" -gt 0 ]; then
            printf "    %-15s %3d commands\n" "$cat_name:" "$cmd_count"
            
            # Show recent commands in this category
            recent=$(find "$category" -name "*.md" -mtime -30 2>/dev/null | wc -l)
            if [ "$recent" -gt 0 ]; then
                echo "      (including $recent from last 30 days)"
            fi
        fi
    fi
done

echo ""
echo "  📊 Curated Summary:"
echo "    📄 Total curated: $curated_total"
echo "    📈 Curation rate: $(echo "scale=1; $curated_total * 100 / $total_commands" | bc 2>/dev/null || echo "N/A")% of available commands"
```

## 🧪 Testing Activity

```bash
echo ""
echo "🔬 Testing Activity:"
echo "==================="

cd ~/claude-code-command-hub/testing

# Count test environments
test_count=$(ls -1d sandbox-* 2>/dev/null | wc -l)
echo "  🧪 Active test environments: $test_count"

if [ "$test_count" -gt 0 ]; then
    echo "  📅 Recent test sessions:"
    ls -1td sandbox-* 2>/dev/null | head -5 | while read -r test_dir; do
        test_date=$(echo "$test_dir" | sed 's/sandbox-//' | sed 's/_/ /')
        echo "    - $test_date"
    done
fi

# Count test results
result_count=$(find test-results/ -name "test-*.md" 2>/dev/null | wc -l)
echo "  📝 Test reports generated: $result_count"

if [ "$result_count" -gt 0 ]; then
    echo "  📊 Recent test activity:"
    find test-results/ -name "test-*.md" -mtime -7 2>/dev/null | wc -l | xargs -I {} echo "    {} tests in last 7 days"
fi
```

## 📈 Usage Patterns

```bash
echo ""
echo "📊 Usage Patterns:"
echo "=================="

# Analyze update history
if [ -f "~/claude-code-command-hub/metadata/update-history.md" ]; then
    sync_count=$(grep -c "Synchronized" ~/claude-code-command-hub/metadata/update-history.md 2>/dev/null || echo 0)
    echo "  🔄 Total sync operations: $sync_count"
    
    # Last sync
    if [ "$sync_count" -gt 0 ]; then
        last_sync=$(grep "Synchronized" ~/claude-code-command-hub/metadata/update-history.md | tail -1 | cut -d':' -f1)
        echo "  📅 Last sync: $last_sync"
    fi
fi

# Registry info
if [ -f "~/claude-code-command-hub/metadata/command-registry.json" ]; then
    echo "  📋 Registry maintained: Yes"
    
    # Try to extract some stats from JSON
    if command -v jq >/dev/null 2>&1; then
        deployed=$(jq -r '.statistics.deployed_commands // 0' ~/claude-code-command-hub/metadata/command-registry.json 2>/dev/null || echo 0)
        echo "  🚀 Deployed commands: $deployed"
    fi
else
    echo "  📋 Registry maintained: No"
fi
```

## 🎯 Popular Command Categories

```bash
echo ""
echo "🔥 Popular Command Categories (by availability):"
echo "================================================"

cd ~/claude-code-command-hub/repositories

# Analyze command patterns across all repositories
for category in dev docs project test security deploy context git; do
    count=$(find . -name "*.md" \( -path "*/commands/*" -o -path "*/.claude/commands/*" \) -exec grep -l -i "$category" {} \; 2>/dev/null | wc -l)
    if [ "$count" -gt 0 ]; then
        printf "  %-12s %3d related commands\n" "$category:" "$count"
    fi
done

echo ""
echo "🏷️ Common command patterns:"
git_count=$(find . -name "*.md" \( -path "*/commands/*" -o -path "*/.claude/commands/*" \) -exec grep -l -i "git\|commit\|push\|pull" {} \; 2>/dev/null | wc -l)
doc_count=$(find . -name "*.md" \( -path "*/commands/*" -o -path "*/.claude/commands/*" \) -exec grep -l -i "doc\|session\|log" {} \; 2>/dev/null | wc -l)
test_count=$(find . -name "*.md" \( -path "*/commands/*" -o -path "*/.claude/commands/*" \) -exec grep -l -i "test\|spec\|check" {} \; 2>/dev/null | wc -l)

echo "  🔧 Git/Version Control: $git_count commands"
echo "  📚 Documentation/Logging: $doc_count commands"
echo "  🧪 Testing/Validation: $test_count commands"
```

## 💡 Recommendations

```bash
echo ""
echo "💡 Recommendations:"
echo "==================="

# Suggest actions based on stats
if [ "$curated_total" -eq 0 ]; then
    echo "  🎯 Start curating: Use /hub:discover to find useful commands"
    echo "  🧪 Test commands: Use /hub:test to safely evaluate commands"
elif [ "$curated_total" -gt 0 ] && [ "$curated_total" -lt 10 ]; then
    echo "  📈 Growing collection: $curated_total curated commands is a good start!"
    echo "  🔍 Keep exploring: Use /hub:discover for more commands"
else
    echo "  🎉 Mature collection: $curated_total curated commands!"
    echo "  🚀 Consider deployment: Use /hub:deploy to add commands to projects"
fi

# Check for stale data
if command -v find >/dev/null 2>&1; then
    old_repos=$(find ~/claude-code-command-hub/repositories -name ".git" -type d -exec test '{}' -ot ~/claude-code-command-hub/repositories \; -print 2>/dev/null | wc -l)
    if [ "$old_repos" -gt 0 ]; then
        echo "  🔄 Update needed: Run /hub:sync to get latest community commands"
    fi
fi

echo ""
echo "🎯 Next steps you might consider:"
echo "  1. /hub:discover - Browse available commands"
echo "  2. /hub:test <command> - Try a specific command"
echo "  3. /hub:sync - Update repositories"
echo "  4. /hub:deploy <project> <category> - Deploy to a project"
```

---

**Statistics complete!** Your command hub is actively managing $total_commands community commands.