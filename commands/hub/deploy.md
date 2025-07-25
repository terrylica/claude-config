---
description: Deploy curated commands to a project
argument-hint: "<project-path> [category]"
allowed-tools: Bash, Write
---

# Deploy Commands: $ARGUMENTS

Deploying curated commands to your project...

## 🎯 Deployment Setup

```bash
args=($ARGUMENTS)
project_path="${args[0]}"
category="${args[1]:-all}"

if [ -z "$project_path" ]; then
    echo "❌ Usage: /hub:deploy <project-path> [category]"
    echo ""
    echo "Examples:"
    echo "  /hub:deploy /path/to/my-project docs"
    echo "  /hub:deploy ~/projects/web-app dev"
    echo "  /hub:deploy . all"
    echo ""
    echo "Available categories:"
    ls -1 ~/claude-code-command-hub/curated/ 2>/dev/null | while read -r cat; do
        if [ -d "~/claude-code-command-hub/curated/$cat" ]; then
            count=$(find ~/claude-code-command-hub/curated/$cat -name "*.md" 2>/dev/null | wc -l)
            echo "  - $cat ($count commands)"
        fi
    done
    echo "  - all (deploy everything)"
    exit 1
fi

# Resolve absolute path
if [[ "$project_path" == /* ]]; then
    abs_project_path="$project_path"
elif [ "$project_path" = "." ]; then
    abs_project_path="$(pwd)"
else
    abs_project_path="$(cd "$project_path" 2>/dev/null && pwd)" || abs_project_path="$project_path"
fi

echo "🎯 Deployment Configuration:"
echo "  📂 Target project: $abs_project_path"
echo "  📋 Category: $category"
echo "  📅 Date: $(date)"
```

## 🔍 Pre-deployment Validation

```bash
# Validate project path
if [ ! -d "$abs_project_path" ]; then
    echo "❌ Project directory does not exist: $abs_project_path"
    echo ""
    echo "💡 Create the directory first or use an existing project path"
    exit 1
fi

echo "✅ Project directory exists"

# Check if it's a git repository (informational)
if [ -d "$abs_project_path/.git" ]; then
    echo "📂 Git repository detected"
    cd "$abs_project_path"
    current_branch=$(git branch --show-current 2>/dev/null || echo "unknown")
    echo "  📌 Current branch: $current_branch"
else
    echo "📁 Not a git repository (that's okay)"
fi

# Validate category
curated_path="$HOME/claude-code-command-hub/curated"

if [ "$category" != "all" ] && [ ! -d "$curated_path/$category" ]; then
    echo "❌ Category '$category' not found in curated collection"
    echo ""
    echo "Available categories:"
    ls -1 "$curated_path" 2>/dev/null | while read -r cat; do
        if [ -d "$curated_path/$cat" ]; then
            count=$(find "$curated_path/$cat" -name "*.md" 2>/dev/null | wc -l)
            echo "  - $cat ($count commands)"
        fi
    done
    exit 1
fi

echo "✅ Category validation passed"
```

## 📦 Command Deployment

```bash
# Create target directory structure
target_commands_dir="$abs_project_path/.claude/commands"
mkdir -p "$target_commands_dir"

echo ""
echo "📦 Deploying commands..."
echo "  📁 Target: $target_commands_dir"

deployed_count=0
backup_created=false

# Create backup if commands already exist
if [ -d "$target_commands_dir" ] && [ "$(find "$target_commands_dir" -name "*.md" 2>/dev/null | wc -l)" -gt 0 ]; then
    backup_dir="$target_commands_dir/../commands-backup-$(date +%Y%m%d_%H%M%S)"
    echo "  💾 Creating backup: $backup_dir"
    cp -r "$target_commands_dir" "$backup_dir"
    backup_created=true
fi

# Deploy based on category
if [ "$category" = "all" ]; then
    echo "  🚀 Deploying all curated commands..."
    
    for cat_dir in "$curated_path"/*; do
        if [ -d "$cat_dir" ]; then
            cat_name=$(basename "$cat_dir")
            cat_count=$(find "$cat_dir" -name "*.md" 2>/dev/null | wc -l)
            
            if [ "$cat_count" -gt 0 ]; then
                echo "    📁 Category: $cat_name ($cat_count commands)"
                
                # Create category subdirectory
                mkdir -p "$target_commands_dir/$cat_name"
                
                # Copy all commands from this category
                find "$cat_dir" -name "*.md" 2>/dev/null | while read -r cmd_file; do
                    cmd_name=$(basename "$cmd_file")
                    cp "$cmd_file" "$target_commands_dir/$cat_name/"
                    echo "      ✅ $cmd_name"
                done
                
                deployed_count=$((deployed_count + cat_count))
            fi
        fi
    done
else
    echo "  🎯 Deploying category: $category"
    
    cat_count=$(find "$curated_path/$category" -name "*.md" 2>/dev/null | wc -l)
    
    if [ "$cat_count" -gt 0 ]; then
        # Create category subdirectory
        mkdir -p "$target_commands_dir/$category"
        
        # Copy commands
        find "$curated_path/$category" -name "*.md" 2>/dev/null | while read -r cmd_file; do
            cmd_name=$(basename "$cmd_file")
            cp "$cmd_file" "$target_commands_dir/$category/"
            echo "    ✅ $cmd_name"
        done
        
        deployed_count="$cat_count"
    else
        echo "    ⚠️  No commands found in category '$category'"
    fi
fi

echo ""
echo "📊 Deployment Summary:"
echo "  📄 Commands deployed: $deployed_count"
echo "  📂 Target location: $target_commands_dir"
if [ "$backup_created" = true ]; then
    echo "  💾 Backup created: ${backup_dir##*/}"
fi
```

## 📋 Post-deployment Steps

```bash
echo ""
echo "📋 Post-deployment Information:"
echo "=============================="

# Show deployed command structure
echo "  🗂️ Deployed command structure:"
cd "$target_commands_dir"
find . -name "*.md" | head -10 | while read -r cmd; do
    cmd_path=${cmd#./}
    echo "    /$cmd_path"
done

total_deployed=$(find . -name "*.md" | wc -l)
if [ "$total_deployed" -gt 10 ]; then
    echo "    ... and $((total_deployed - 10)) more commands"
fi

# Test command availability
echo ""
echo "  🧪 Command Availability Test:"
echo "    To test the deployed commands:"
echo "    1. cd $abs_project_path"
echo "    2. claude"
echo "    3. Type '/' to see available commands"

# Git integration (if applicable)
if [ -d "$abs_project_path/.git" ]; then
    echo ""
    echo "  📝 Git Integration:"
    echo "    Commands are ready to commit:"
    echo "    cd $abs_project_path"
    echo "    git add .claude/commands/"
    echo "    git commit -m 'Add Claude Code commands from hub'"
    echo ""
    echo "    This will share the commands with your team!"
fi
```

## 📊 Deployment Logging

```bash
# Log the deployment
deploy_log="$HOME/claude-code-command-hub/metadata/deployment-log.md"
deploy_time=$(date -Iseconds)

echo ""
echo "📝 Logging deployment..."

# Append to deployment log
cat >> "$deploy_log" << EOF

## Deployment: $deploy_time

- **Project**: $abs_project_path
- **Category**: $category  
- **Commands Deployed**: $deployed_count
- **Backup Created**: $backup_created

### Commands Deployed:
EOF

# List deployed commands
if [ "$category" = "all" ]; then
    for cat_dir in "$curated_path"/*; do
        if [ -d "$cat_dir" ]; then
            cat_name=$(basename "$cat_dir")
            find "$cat_dir" -name "*.md" 2>/dev/null | while read -r cmd_file; do
                cmd_name=$(basename "$cmd_file" .md)
                echo "- /$cat_name:$cmd_name" >> "$deploy_log"
            done
        fi
    done
else
    find "$curated_path/$category" -name "*.md" 2>/dev/null | while read -r cmd_file; do
        cmd_name=$(basename "$cmd_file" .md)
        echo "- /$category:$cmd_name" >> "$deploy_log"
    done
fi

echo "" >> "$deploy_log"

echo "✅ Deployment logged to: $deploy_log"
```

## 🎯 Usage Instructions

```bash
echo ""
echo "🎯 How to Use Your Deployed Commands:"
echo "===================================="
echo ""
echo "1. Navigate to your project:"
echo "   cd $abs_project_path"
echo ""
echo "2. Start Claude Code:"
echo "   claude"
echo ""
echo "3. Use your commands:"
if [ "$category" = "all" ]; then
    echo "   Type '/' to see all available commands"
    echo "   Commands are organized by namespace (e.g., /docs:command, /dev:command)"
else
    echo "   Type '/' to see available commands"
    echo "   Your commands are in the /$category: namespace"
fi
echo ""
echo "4. Share with your team (if git repo):"
echo "   git add .claude/commands/ && git commit -m 'Add Claude commands'"
echo ""
echo "💡 Pro tip: Commands are immediately available in Claude Code!"
```

## 🔄 Rollback Information

```bash
if [ "$backup_created" = true ]; then
    echo ""
    echo "🔄 Rollback Instructions (if needed):"
    echo "===================================="
    echo ""
    echo "If you need to undo this deployment:"
    echo "  rm -rf $target_commands_dir"
    echo "  mv $backup_dir $target_commands_dir"
    echo ""
    echo "💾 Backup location: $backup_dir"
fi
```

---

**Deployment complete!** Your curated commands are now available in the target project. Navigate to the project and start Claude Code to use them.