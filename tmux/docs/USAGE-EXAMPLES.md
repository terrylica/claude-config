# Claude Code tmux Integration - Usage Examples

Real-world usage patterns and workflows demonstrating the intelligent session management system.

## 🎯 **Zero-Config Basic Usage**

### **First-Time User Experience**
```bash
# Day 1: Start new project
cd ~/my-new-api
claude "help me design a REST API for a task management app"
# → Automatically creates: claude-default-my-new-api-a1b2c3
# → User sees normal Claude interface, no complexity

# Work continues...
claude --model gpt-4 "now help me implement user authentication" 
# → Same session, conversation continues seamlessly

# Terminal crashes or user closes it
# Day 2: Resume work
cd ~/my-new-api
claude "let's continue where we left off with the API"
# → Automatically attaches to: claude-default-my-new-api-a1b2c3
# → Full conversation history preserved
```

### **Multiple Projects, Zero Overhead**
```bash
# Morning: Work on API project
cd ~/projects/task-api
claude "help me implement the database schema"
# → Creates: claude-default-task-api-x1y2z3

# Afternoon: Switch to frontend
cd ~/projects/task-frontend  
claude "help me build the React components"
# → Creates: claude-default-task-frontend-m4n5o6

# Evening: Back to API
cd ~/projects/task-api
claude "help me add validation middleware"
# → Resumes: claude-default-task-api-x1y2z3 (same conversation)
```

## 🚀 **Advanced Multi-Session Workflows**

### **Feature Development with Named Sessions**
```bash
cd ~/my-project

# Start focused session for authentication feature
claude-session start auth
claude --debug "help me implement OAuth2 with refresh tokens"
# → Creates: claude-auth-my-project-a1b2c3

# Detach and start session for bug fixing
# Ctrl+b d (or close terminal)
claude-session start bugfix  
claude "help me debug this database connection issue"
# → Creates: claude-bugfix-my-project-a1b2c3

# Later: Which session to resume?
claude "help me optimize the API performance"
# → Prompt appears:
#   🎯 Multiple Claude sessions found for my-project:
#   1) default (yesterday, 1w, ⚫ detached)
#   2) auth (2 hours ago, 2w, ⚫ detached)  
#   3) bugfix (30 minutes ago, 1w, ⚫ detached)
#   Select session [3]: 2
# → Resumes auth session
```

### **Team Collaboration with Consistent Naming**
```bash
# Team agrees on session naming conventions
cd ~/shared-project

# Backend developer
claude-session start backend-api
claude "help me design the user service endpoints"

# Frontend developer  
claude-session start frontend-components
claude "help me create reusable UI components"

# DevOps engineer
claude-session start deployment
claude "help me set up CI/CD pipeline"

# Later: Easy to find relevant sessions
claude-session list
# Shows:
#   TYPE                | WINDOWS | LAST ACTIVITY   | STATUS
#   backend-api         | 2w      | 5 minutes ago   | ⚫ detached
#   frontend-components | 1w      | 1 hour ago      | ⚫ detached  
#   deployment          | 3w      | 2 hours ago     | 🟢 active
```

## 🔧 **Compatibility with All Claude Code Features**

### **All Flags Work Identically**
```bash
# Model selection - works in sessions
claude --model gpt-4 "help me with complex algorithms"
claude --model claude-3 "help me write documentation"

# Debug mode - works in sessions  
claude --debug --verbose "help me troubleshoot this issue"

# Permission modes - works in sessions
claude --permission-mode plan "help me design the architecture"

# Tool restrictions - works in sessions
claude --allowedTools "Bash Edit" "help me refactor this code"
claude --disallowedTools "WebFetch" "help me with local development"

# System prompts - works in sessions
claude --append-system-prompt "Be concise and direct" "help me optimize this"
```

### **Non-Interactive Modes (No Sessions)**
```bash
# Quick queries - run directly, no tmux overhead
claude --print "what's the syntax for async/await in Python?"
claude --output-format json --print "explain REST principles"

# Utility commands - run directly
claude config set model gpt-4
claude mcp add myserver ./server.js
claude doctor
claude update

# These bypass session management entirely for optimal performance
```

### **Session Conflict Handling**
```bash
# Claude's built-in session management
claude --continue
# → Prompt appears:
#   ⚠️ Session Management Conflict Detected
#   
#   You're using Claude's built-in session management (--continue)
#   which conflicts with tmux persistence.
#   
#   Options:
#     1) Use Claude's session management (run directly, no tmux)
#     2) Use tmux persistence (ignore Claude's session flags)
#   Choose option [1]: 

claude --resume session-abc-123
# → Same conflict resolution prompt

# Explicit session IDs - handled gracefully
claude --session-id 12345678-abcd-ef00-1234-567890abcdef "help me"
# → Prompts user for preference
```

## 📊 **Session Management Workflows**

### **Daily Development Routine**
```bash
# Morning: Check what sessions exist
claude-session list
#   TYPE     | WINDOWS | LAST ACTIVITY | STATUS
#   default  | 1w      | yesterday     | ⚫ detached
#   auth     | 2w      | 2 days ago    | ⚫ detached

# Resume where I left off
claude-session attach auth
# Back in authentication context

# Create new session for today's bug fixes
claude-session start hotfix-123
claude "help me fix the login validation bug"

# End of day: Check what's active
claude-session status
#   📊 System Information:
#   Current workspace: my-project
#   Total Claude sessions: 3
#   Workspace sessions: 3
```

### **Session Maintenance**
```bash
# Weekly cleanup - remove old sessions
claude-session clean 7  # Remove sessions older than 7 days

# Spring cleaning - remove all workspace sessions
claude-session kill --all

# Check system health
claude-session status
#   📈 Session Statistics:
#   Total Claude sessions: 12
#   Workspace sessions: 3
#   
#   📜 Recent Activity:
#   2025-01-25 14:30:21 | created  | claude-auth-project-a1b2c3
#   2025-01-25 16:45:12 | attached | claude-default-project-a1b2c3
```

## 🔍 **Troubleshooting and Diagnostics**

### **Debug Common Issues**
```bash
# Check installation health
claude-debug
#   🔍 Claude tmux Integration Debug Info
#   =====================================
#   
#   📊 System Information:
#   OS: Darwin
#   Shell: /bin/zsh
#   tmux: tmux 3.2a
#   Claude Code: Available
#   
#   📁 Installation:
#   Base directory: /Users/terry/.claude/tmux
#   Router script: ✅ Present
#   Session manager: ✅ Present
#   Integration loaded: ✅ Yes

# Check for old configurations
claude-migrate
#   🔄 Claude tmux Integration Migration
#   Old files found:
#     - /Users/terry/.claude/tmux_claude_manager.sh
#   
#   These files are no longer used. You can safely remove them.

# Show current workspace context
claude-workspace
#   📁 Current Workspace: my-project
#   🔍 Path Hash: a1b2c3
#   📂 Full Path: /Users/terry/projects/my-project
#   
#   🎯 Multiple Claude sessions found for my-project:
#   [... session list ...]
```

### **Configuration Management**
```bash
# Show workspace configuration
claude-session config show
#   🔧 Workspace Configuration:
#   {
#     "workspace_name": "my-project",
#     "workspace_path": "/Users/terry/projects/my-project",
#     "default_session": "",
#     "created_sessions": ["default", "auth", "bugfix"]
#   }

# Set default session for workspace
claude-session config set default_session auth

# Reset configuration to defaults
claude-session config reset
```

## 🎨 **Advanced Usage Patterns**

### **IDE Integration**
```bash
# Use with IDE integration (if compatible)
claude --ide "help me refactor this class"
# → Creates session and attempts IDE connection

# VS Code workflow
cd ~/my-project
claude-session start vscode-work
claude "help me set up debugging for Node.js"
# → Session persists even when VS Code restarts
```

### **Long-Running Development Sessions**
```bash
# Start comprehensive development session
cd ~/complex-project
claude-session start main-dev
claude "I'm working on a large refactoring project. Let's start by analyzing the current architecture."

# Multiple days later, session preserves full context
claude-session attach main-dev
claude "continuing from our architecture analysis, let's now implement the new design patterns we discussed"
# → Full conversation history available
```

### **Project-Specific Workflows**
```bash
# Machine learning project
cd ~/ml-research
claude-session start experiment-1
claude --model gpt-4 "help me design experiments for testing this new algorithm"

# Web development project
cd ~/webapp
claude-session start frontend
claude "help me implement responsive design patterns"
claude-session start backend  
claude "help me optimize database queries"

# Each context maintained separately with full conversation history
```

## 💡 **Best Practices**

### **Session Naming Conventions**
```bash
# Feature-based naming
claude-session start user-auth
claude-session start payment-system
claude-session start admin-panel

# Ticket/issue-based naming
claude-session start bug-1234
claude-session start feature-5678
claude-session start hotfix-security

# Time-based naming for exploration
claude-session start research-jan25
claude-session start prototype-2025
```

### **Workflow Organization**
```bash
# Keep default session for general work
claude "quick question about syntax"  # → uses default session

# Create focused sessions for complex tasks
claude-session start complex-feature
claude "let's dive deep into implementing this complex authentication system"

# Use session management for context switching
claude-session list  # → see all contexts
claude-session attach relevant-context  # → switch to specific context
```

### **Maintenance Routines**
```bash
# Daily: Check active sessions
claude-sessions

# Weekly: Clean old sessions  
claude-session clean 7

# Monthly: Full system status
claude-session status
claude-debug

# Project completion: Clean workspace sessions
claude-session kill --all
```

---

This integration provides **invisible persistence** for your Claude Code workflows while maintaining **100% compatibility** with all Claude features. The system scales from zero-config simplicity to advanced multi-session project management, adapting to your development needs without cognitive overhead.