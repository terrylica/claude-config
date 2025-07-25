---
description: Test a command safely in isolated environment
argument-hint: "<command-file-path>"
allowed-tools: Bash, Read, Write
---

# Test Command: $ARGUMENTS

Setting up safe testing environment for command evaluation...

## 🔍 Command Validation

```bash
command_file="$ARGUMENTS"

if [ -z "$command_file" ]; then
    echo "❌ Usage: /hub:test <command-file-path>"
    echo ""
    echo "Examples:"
    echo "  /hub:test Claude-Command-Suite/commands/dev/code-review.md"
    echo "  /hub:test awesome-claude-code/commands/docs/session-start.md"
    echo ""
    echo "💡 Use /hub:discover to find available commands"
    exit 1
fi

# Resolve full path
if [[ "$command_file" == /* ]]; then
    # Absolute path
    full_path="$command_file"
else
    # Relative path - check if it starts with repo name or needs hub prefix
    if [ -f "~/claude-code-command-hub/repositories/$command_file" ]; then
        full_path="$HOME/claude-code-command-hub/repositories/$command_file"
    elif [ -f "$command_file" ]; then
        full_path="$command_file"
    else
        full_path="$HOME/claude-code-command-hub/repositories/$command_file"
    fi
fi

if [ ! -f "$full_path" ]; then
    echo "❌ Command file not found: $command_file"
    echo ""
    echo "🔍 Searching for similar files..."
    filename=$(basename "$command_file")
    find ~/claude-code-command-hub/repositories/ -name "*$filename*" -type f 2>/dev/null | head -5 | while read -r found_file; do
        rel_path=${found_file#$HOME/claude-code-command-hub/repositories/}
        echo "  📄 $rel_path"
    done
    echo ""
    echo "💡 Use /hub:discover to browse available commands"
    exit 1
fi

echo "✅ Command file found: $full_path"
command_name=$(basename "$command_file" .md)
```

## 🧪 Setup Test Environment

```bash
cd ~/claude-code-command-hub/testing

# Create isolated sandbox with timestamp
test_id=$(date +%Y%m%d_%H%M%S)
test_dir="sandbox-$test_id"

echo "🔬 Creating test environment: $test_dir"

# Clean up old test directories (keep last 5)
echo "🧹 Cleaning up old test environments..."
ls -1d sandbox-* 2>/dev/null | head -n -5 | xargs rm -rf 2>/dev/null || true

# Create fresh sandbox
rm -rf "$test_dir"
mkdir -p "$test_dir"/.claude/commands

# Copy command for testing
cp "$full_path" "$test_dir/.claude/commands/"

echo "✅ Test environment ready: ~/claude-code-command-hub/testing/$test_dir"
```

## 📄 Command Analysis

```bash
echo ""
echo "📋 Command Analysis:"
echo "===================="

# Extract metadata
echo "📌 Command: /$command_name"
echo "📁 Source: $command_file"
echo "📝 Size: $(wc -c < "$full_path") bytes"

# Show frontmatter if present
if grep -q "^---" "$full_path"; then
    echo ""
    echo "⚙️ Configuration:"
    sed -n '/^---$/,/^---$/p' "$full_path" | grep -v "^---$" | while read -r line; do
        echo "  $line"
    done
fi

# Extract description
echo ""
echo "📖 Command Preview:"
echo "==================="
head -20 "$full_path" | tail -n +1

# Check for required tools
echo ""
echo "🔧 Tool Requirements:"
if grep -q "allowed-tools:" "$full_path"; then
    tools=$(grep "allowed-tools:" "$full_path" | head -1 | sed 's/allowed-tools: *//g')
    echo "  Required: $tools"
else
    echo "  No specific tool restrictions"
fi

# Check for arguments
if grep -q "argument-hint:" "$full_path"; then
    args=$(grep "argument-hint:" "$full_path" | head -1 | sed 's/argument-hint: *//g' | tr -d '"')
    echo "  Arguments: $args"
fi

# Look for potential security concerns
echo ""
echo "🛡️ Security Check:"
if grep -i -E "(rm -rf|sudo|curl.*sh|wget.*sh|\$\(.*\)|eval)" "$full_path" >/dev/null 2>&1; then
    echo "  ⚠️  Command contains potentially dangerous operations"
    echo "  🔍 Found patterns:"
    grep -n -i -E "(rm -rf|sudo|curl.*sh|wget.*sh|\$\(.*\)|eval)" "$full_path" | head -3 | while read -r line; do
        echo "    Line: $line"
    done
else
    echo "  ✅ No obvious security concerns detected"
fi
```

## 🎯 Testing Instructions

```bash
echo ""
echo "🎯 How to Test This Command:"
echo "============================"
echo ""
echo "1. Navigate to test environment:"
echo "   cd ~/claude-code-command-hub/testing/$test_dir"
echo ""
echo "2. Start Claude Code in the test directory:"
echo "   claude"
echo ""
echo "3. Run the command:"
echo "   /$command_name"

# Add argument hints if available
if grep -q "argument-hint:" "$full_path"; then
    args=$(grep "argument-hint:" "$full_path" | head -1 | sed 's/argument-hint: *//g' | tr -d '"')
    echo "   (with arguments: $args)"
fi

echo ""
echo "4. Observe the results and test behavior"
echo ""
echo "5. Exit Claude Code when done (Ctrl+C or /exit)"
```

## 📊 Test Environment Details

```bash
echo ""
echo "🔍 Test Environment Details:"
echo "============================="
echo "  📂 Location: ~/claude-code-command-hub/testing/$test_dir"
echo "  🕒 Created: $(date)"
echo "  📄 Command: /$command_name"
echo "  🗂️ Files in test environment:"

cd "$test_dir"
find . -type f | while read -r file; do
    echo "    $file"
done

echo ""
echo "  📁 Directory structure:"
tree -a . 2>/dev/null || find . -type d | sed 's|[^/]*/|  |g'
```

## 📝 Test Logging

```bash
# Prepare test result logging
echo ""
echo "📝 Test Logging:"
echo "================"

test_log="~/claude-code-command-hub/testing/test-results/test-$test_id.md"
mkdir -p ~/claude-code-command-hub/testing/test-results

cat > "$test_log" << EOF
# Test Report: $command_name

**Test ID**: $test_id  
**Date**: $(date)  
**Command**: /$command_name  
**Source**: $command_file  
**Test Environment**: ~/claude-code-command-hub/testing/$test_dir

## Command Details
\`\`\`
$(head -10 "$full_path")
...
\`\`\`

## Test Results
<!-- Fill in after testing -->

### Execution
- [ ] Command executed successfully
- [ ] No errors encountered  
- [ ] Behavior matches expectations

### Evaluation
- [ ] Command is useful for my workflow
- [ ] Ready for curation
- [ ] Needs modifications

### Notes
<!-- Add your testing notes here -->

EOF

echo "  📄 Test log prepared: $test_log"
echo "  📝 Update the log file with your test results"
```

## ⏭️ Next Steps

```bash
echo ""
echo "⏭️ After Testing:"
echo "=================="
echo ""
echo "If the command works well:"
echo "  1. Copy to curated collection:"
echo "     cp .claude/commands/$command_name.md ~/claude-code-command-hub/curated/<category>/"
echo ""
echo "  2. Use /hub:curate to organize it properly"
echo ""
echo "  3. Deploy to your projects:"
echo "     /hub:deploy /path/to/project <category>"
echo ""
echo "If the command needs work:"
echo "  1. Edit the command file in the test environment"
echo "  2. Test your modifications"
echo "  3. Save the improved version to curated/"
echo ""
echo "🧹 Cleanup:"
echo "  - Test environments are automatically cleaned (keeps last 5)"
echo "  - Or manually: rm -rf ~/claude-code-command-hub/testing/$test_dir"
```

---

**Test environment ready!** Navigate to the test directory and start Claude Code to try the command safely.