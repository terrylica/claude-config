---
description: Synchronize all community command repositories
allowed-tools: Bash
---

# Sync Claude Code Command Hub

Synchronizing all community repositories and updating command registry...

## Repository Updates

```bash
cd ~/claude-code-command-hub/repositories

echo "🔄 Syncing community repositories..."
echo "Started at: $(date)"

# Update awesome-claude-code
echo ""
echo "📚 Syncing awesome-claude-code..."
if [ -d "awesome-claude-code" ]; then
    echo "  Updating existing repository..."
    cd awesome-claude-code
    git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || echo "  ⚠️  Pull failed, but repository exists"
    cd ..
else
    echo "  Cloning repository..."
    git clone https://github.com/hesreallyhim/awesome-claude-code.git 2>/dev/null || echo "  ⚠️  Clone failed"
fi

# Update Claude Command Suite
echo ""
echo "⚙️ Syncing Claude-Command-Suite..."
if [ -d "Claude-Command-Suite" ]; then
    echo "  Updating existing repository..."
    cd Claude-Command-Suite
    git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || echo "  ⚠️  Pull failed, but repository exists"
    cd ..
else
    echo "  Cloning repository..."
    git clone https://github.com/qdhenry/Claude-Command-Suite.git 2>/dev/null || echo "  ⚠️  Clone failed"
fi

# Update other popular repositories
echo ""
echo "🔧 Syncing additional repositories..."

repos=(
    "vincenthopf/claude-code"
    "disler/claude-code-hooks-mastery"
    "centminmod/my-claude-code-setup"
)

for repo in "${repos[@]}"; do
    dir_name=$(basename "$repo")
    echo "  Processing $dir_name..."
    if [ -d "$dir_name" ]; then
        cd "$dir_name"
        git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || echo "    ⚠️  Pull failed, but repository exists"
        cd ..
    else
        git clone "https://github.com/$repo.git" "$dir_name" 2>/dev/null || echo "    ⚠️  Clone failed for $repo"
    fi
done

# Update NPM command registry
echo ""
echo "📦 Updating claude-cmd registry..."
claude-cmd update 2>/dev/null && echo "  ✅ claude-cmd updated" || echo "  ℹ️  claude-cmd not installed (optional)"

echo ""
echo "✅ Repository sync complete at $(date)"
```

## Command Discovery

```bash
echo ""
echo "🔍 Scanning for commands..."

cd ~/claude-code-command-hub/repositories

# Count total commands
total_commands=$(find . -name "*.md" -path "*/commands/*" -o -path "*/.claude/commands/*" 2>/dev/null | wc -l)
echo "📊 Found $total_commands total commands across all repositories"

# Show recent additions (last 7 days)
echo ""
echo "🆕 Recent additions (last 7 days):"
recent_count=$(find . -name "*.md" \( -path "*/commands/*" -o -path "*/.claude/commands/*" \) -mtime -7 2>/dev/null | wc -l)
if [ "$recent_count" -gt 0 ]; then
    find . -name "*.md" \( -path "*/commands/*" -o -path "*/.claude/commands/*" \) -mtime -7 2>/dev/null | \
        head -10 | \
        sed 's|^\./||' | \
        sed 's|^|  - |'
else
    echo "  No new commands in the last 7 days"
fi

# Show command distribution
echo ""
echo "📈 Command distribution by source:"
for repo_dir in */; do
    if [ -d "$repo_dir" ]; then
        repo_name=${repo_dir%/}
        cmd_count=$(find "$repo_dir" -name "*.md" \( -path "*/commands/*" -o -path "*/.claude/commands/*" \) 2>/dev/null | wc -l)
        if [ "$cmd_count" -gt 0 ]; then
            echo "  - $repo_name: $cmd_count commands"
        fi
    fi
done
```

## Update Registry

```bash
echo ""
echo "📋 Updating command registry..."

cd ~/claude-code-command-hub

# Update metadata
sync_time=$(date -Iseconds)
echo "$sync_time: Synchronized all repositories" >> metadata/update-history.md
echo "- Total repositories: $(find repositories/ -maxdepth 1 -type d 2>/dev/null | wc -l)" >> metadata/update-history.md
echo "- Total commands: $total_commands" >> metadata/update-history.md

# Update JSON registry (basic update)
cat > metadata/command-registry.json << EOF
{
  "version": "1.0.0",
  "created": "2025-01-23T10:30:00Z",
  "last_updated": "$sync_time",
  "repositories": {},
  "commands": {},
  "statistics": {
    "total_repositories": $(find repositories/ -maxdepth 1 -type d 2>/dev/null | tail -n +2 | wc -l),
    "total_commands": $total_commands,
    "curated_commands": $(find curated/ -name "*.md" 2>/dev/null | wc -l),
    "deployed_commands": 0
  },
  "sync_history": ["$sync_time"],
  "deployment_history": []
}
EOF

echo "✅ Registry updated successfully"
```

## Next Steps

```bash
echo ""
echo "🎯 Next steps:"
echo "  1. Run '/hub:discover' to browse available commands"
echo "  2. Use '/hub:test <command-file>' to safely test commands"
echo "  3. Move good commands to curated/ collection"
echo "  4. Deploy to projects with '/hub:deploy <project> <category>'"
echo ""
echo "📚 Hub location: ~/claude-code-command-hub/"
echo "🔍 Browse commands: find ~/claude-code-command-hub/repositories/ -name '*.md' -path '*/commands/*'"
```

---

**Sync complete!** Your command hub is now up to date with the latest community commands.