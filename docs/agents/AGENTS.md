# Agents Directory

**Purpose**: Custom agent configurations and specialized agents for Claude Code

## Available Agents

### [Research Scout](../../agents/research-scout.md) (`research-scout`)
Explores research directions from seed keywords. Use when you need systematic exploration of topics.

### [Context-Bound Planner](../../agents/context-bound-planner.md) (`context-bound-planner`)
Planning assistant that keeps solutions tied to explicit context, constraints, and invariants.

<!-- Pruned to only list agents present in /agents/ -->

## Usage
Use agents with the Task tool:
```
Task(description="Research task", prompt="Your request", subagent_type="research-scout")
```

## ⚠️ CRITICAL: Agent Directory Requirements

### Frontmatter Requirements
**ALL agent files MUST include these required fields:**
```yaml
---
name: agent-name
description: "Agent description"
tools: Tool1, Tool2, Tool3
---
```

**Missing `name` field will cause parsing failures.**

### Directory Purity Rules
- **ONLY agent `.md` files** belong in `/agents/` directory
- **NO documentation files** (README.md, guides, etc.)
- **NO non-agent content** - everything gets parsed as an agent

### Documentation Placement
- **Agent documentation** → `/docs/AGENTS.md` (this file)
- **Command documentation** → `/commands/` directory  
- **General docs** → `/docs/` directory

### Common Mistakes That Cause Parsing Failures
1. ❌ `README.md` in `/agents/` directory → Move to `/docs/AGENTS.md`
2. ❌ Missing `name:` field in frontmatter → Add required field
3. ❌ Documentation files in `/agents/` → Move to appropriate `/docs/` location
4. ❌ Non-agent `.md` files in `/agents/` → Move or rename

## Claude Code Official Status
❌ **USER DIRECTORY** - Safe to customize and modify

This directory contains user-defined agents and is not part of Claude Code's core functionality.
