# Agents Documentation

## Overview

Custom Claude Code agents for specialized tasks are defined in `/Users/terryli/.claude/agents/` as markdown files with YAML frontmatter.

## Status

Currently, all custom agents have been disabled to reduce context consumption. See [`/Users/terryli/.claude/agents-disabled/`](/Users/terryli/.claude/agents-disabled/) for archived agent definitions.

## Available Agents

Custom agents are currently disabled. The workspace uses built-in Claude Code agents accessible via the Task tool.

## Creating Custom Agents

Custom agents can be defined as markdown files with YAML frontmatter in the agents directory.

### Agent Structure

```markdown
---
name: agent-name
description: Brief description
tools: [Tool1, Tool2]
color: blue
---

# Agent Name

Detailed instructions and process documentation...
```

## Disabled Agents

Archived agents (saved context: 419 tokens):

- `context-bound-planner.md` - Planning agent for context-aware task breakdown
- `research-scout.md` - Research automation agent

To re-enable an agent, move it from `agents-disabled/` to `agents/` directory.

## References

- [Agent Registry](AGENTS.md) - Complete agent documentation
- [Disabled Agents](/Users/terryli/.claude/agents-disabled/) - Archived agent definitions
