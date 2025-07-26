---
description: GitHub Flavored Markdown link integrity checker
argument-hint: "[workspace-path] [--format text|json] [--no-external]"
allowed-tools: Bash
---

# GFM Link Checker: $ARGUMENTS

```bash
# Parse arguments
args=($ARGUMENTS)
workspace_path="${args[0]:-$(pwd)}"

# Build command arguments
cmd_args="$workspace_path"
for arg in "${args[@]:1}"; do
    cmd_args="$cmd_args $arg"
done

# Run the GFM link checker Python script with uv from project directory
cd ~/.claude/tools/gfm-link-checker && uv run python gfm_link_checker.py $cmd_args
```