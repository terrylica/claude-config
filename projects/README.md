# Project Memory

Cross-session context and state persistence for Claude Code workflows.

## Structure

This directory contains project-specific memory files organized by workspace path:

- **Session Files**: `.jsonl` files containing conversation history and context
- **Workspace Organization**: Directories named by escaped workspace paths
- **State Persistence**: Maintains context across Claude Code sessions

## Usage

Project memory is automatically managed by Claude Code. Each workspace gets isolated session storage for context retention between interactions.
