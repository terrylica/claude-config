# Custom Agents

This directory contains custom Claude Code agents for specialized tasks.

## Status

Currently, all custom agents have been disabled to reduce context consumption. See [`agents-disabled/`](../agents-disabled/) for archived agent definitions.

## Available Agents

Custom agents are currently disabled. The workspace uses built-in Claude Code agents accessible via the Task tool.

## Creating Custom Agents

Custom agents can be defined as markdown files with YAML frontmatter. See [Agent Documentation](../docs/agents/AGENTS.md) for the complete agent registry and development guide.

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

- [Agent Registry](../docs/agents/AGENTS.md) - Complete agent documentation
- [Agent Development Guide](../docs/agents/README.md) - Creating and maintaining agents
- [Disabled Agents](../agents-disabled/) - Archived agent definitions
