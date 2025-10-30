# Claude Code Workspace Documentation Index

**Hub-and-Spoke Documentation Architecture**
Central navigation point for all workspace documentation with direct links to module-specific guides.

---

## **🏗️ Core Architecture**

- **[Architecture Overview](architecture/ARCHITECTURE.md)** - Workspace structure and design patterns
- **[Workflow Orchestration Research](architecture/workflow-orchestration-comparison.md)** - Event-driven architecture solutions for Claude Code CLI workflows
- **[Task Queue Research](architecture/lightweight-async-task-queue-research.md)** - Lightweight async task queue systems without external services (Redis/RabbitMQ)
- **[Task Queue Quick Reference](architecture/task-queue-quick-reference.md)** - Quick start guide for persist-queue with SQLite
- **[Task Queue Architecture Diagrams](architecture/task-queue-architecture-diagrams.md)** - Visual comparison of file-based vs SQLite queue architectures
- **[Standards & Guidelines](standards/)** - Development standards and best practices
- **[Tool Organization Standards](standards/TOOL_ORGANIZATION.md)** - Tool taxonomy, decision tree, development workflow

## **🤖 Agent System**

- **[Agent Registry](agents/AGENTS.md)** - Available agents and their capabilities
- **[Agent Development](agents/)** - Creating and maintaining agents

## **⚙️ Tools & Utilities**

- **[Tool Management](../install-all-tools)** - Installation and maintenance of workspace tools
- **[Tmux Integration](../tmux/docs/README.md)** - Terminal multiplexer configuration and usage
- **[GFM Link Checker](../gfm-link-checker/)** - Documentation link validation
- **[Automation System](../automation/)** - CNS and other automated processes

## **🔧 Configuration & Setup**

- **[Setup Guide](setup/TEAM_SETUP.md)** - Team onboarding and workspace setup
- **[Credential Management](setup/aws-credentials-doppler.md)** - AWS credentials with Doppler (rotation, usage, elimination)
- **[Session Management](standards/CLAUDE_SESSION_STORAGE_STANDARD.md)** - Session storage standards
- **[Sync Strategy](sync/claude-code-sync-strategy.md)** - Cross-environment synchronization

## **📊 Project Management**

- **[SAGE Aliases](../sage-aliases/)** - Development environment shortcuts
- **[Todo Management](../todos/)** - Task tracking and progress management
- **[Tool Manifest](../tools/tool-manifest.yaml)** - Machine-readable registry of all workspace tools

## **📈 Reports & Analysis**

- **[MHR Reports](reports/MHR_SAGE_SYNC_REPORT.md)** - Module housekeeping and refactoring reports
- **[System Reports](reports/)** - Various system analysis reports

## **🔧 Workspace Reorganization**

### Specifications

- **[Reorganization Specification](../specifications/workspace-reorganization.yaml)** - Target architecture, migration rules, retention policies
- **[Complete Move Map](../specifications/reorg-move-map.yaml)** - 28 file operations with dependencies and validation
- **[Cleanup Targets](../specifications/reorg-cleanup-targets.yaml)** - 12 cleanup operations with safety protocols
- **[Health Check Specification](../specifications/workspace-health-check.yaml)** - 42 validation checks across 8 categories
- **[Execution Checklists](../specifications/reorg-execution-checklists.yaml)** - Pre/phase/post migration checklists

### Documentation

- **[Migration Guide](maintenance/WORKSPACE_REORGANIZATION_GUIDE.md)** - Step-by-step execution instructions
- **[Artifact Retention Policy](maintenance/ARTIFACT_RETENTION.md)** - 30-day retention with automated archival
- **[Rollback Procedures](maintenance/REORGANIZATION_ROLLBACK.md)** - Phase-by-phase safety procedures

### Status

- **Phase 1**: ✅ Documentation Complete (October 2025)
- **Current Score**: 7.2/10 → **Target**: 9.0/10
- **Space Recovery**: ~150-200 MB from artifact archival
- **Next Step**: Review documentation, then execute Phase 2

## **📚 Reference Materials**

- **[Legacy Archive Notice](../LEGACY_ARCHIVE_NOTICE.md)** - Information about archived legacy systems
- **[Official File Standards](standards/CLAUDE_CODE_OFFICIAL_FILES.md)** - File management guidelines

---

## **🔍 Quick Navigation**

### By Component Type

- **Agents**: [Registry](agents/AGENTS.md) | [Development](agents/)
- **Tools**: [Installation](../install-all-tools) | [Tmux](../tmux/) | [GFM Checker](../gfm-link-checker/)
- **Configuration**: [Standards](standards/) | [Setup](setup/) | [Sync](sync/)

### By Task Type

- **Getting Started**: [Team Setup](setup/TEAM_SETUP.md) → [Architecture](architecture/ARCHITECTURE.md) → [Standards](standards/)
- **Development**: [Agent Registry](agents/AGENTS.md) → [Tool Installation](../install-all-tools) → [SAGE Aliases](../sage-aliases/)
- **Maintenance**: [Reports](reports/) → [Legacy Management](../LEGACY_ARCHIVE_NOTICE.md) → [Standards](standards/)

---

**Navigation Tip**: Each section maintains its own detailed README with module-specific information while this index provides workspace-wide navigation.
