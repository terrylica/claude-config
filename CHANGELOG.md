## [6.0.0] - 2025-10-31

### 🚜 Refactor

- [**breaking**] Migrate to iTerm2 and remove Zellij/Ghostty/tmux
## [6.0.0] - 2025-10-31

### 🐛 Bug Fixes

- *(hook)* Add missing tac pipe to reverse transcript order

### 📚 Documentation

- *(lychee)* Add v5.13.5 CRITICAL fix to CHANGELOG
## [5.13.4] - 2025-10-31

### 🐛 Bug Fixes

- *(hook)* Skip messages starting with ❓ emoji
- *(hook)* Use Unicode escape for emoji to avoid encoding issues
- *(hook)* Filter out emoji-prefixed lines with grep

### 📚 Documentation

- *(lychee)* Add v5.13.4 to CHANGELOG
## [5.13.3] - 2025-10-31

### 🐛 Bug Fixes

- *(hook)* Escape backticks to prevent command substitution
- *(hook)* Skip messages starting with code fence

### 📚 Documentation

- *(lychee)* Add v5.13.2 to implementation plan
- *(lychee)* Add v5.13.3 to CHANGELOG
## [5.13.2] - 2025-10-31

### 🐛 Bug Fixes

- *(hook)* Use first() to select most recent user message

### 📚 Documentation

- *(lychee)* Update plan with v5.13.1 final commit
## [5.13.1] - 2025-10-31

### 🐛 Bug Fixes

- *(hook)* Preserve multi-line user prompts in Stop hook (v5.13.1)
- *(hook)* Filter Telegram echo to extract actual user prompts
- *(hook)* Extract user comments from quoted notifications

### 📚 Documentation

- Mark all phases complete in SSoT plan file
- *(lychee)* Update plan with v5.13.1 Telegram echo fix
## [5.13.0] - 2025-10-31

### 🚀 Features

- *(bot)* Conversation state persistence with PicklePersistence (v5.13.0)
## [5.12.0] - 2025-10-31

### 🚀 Features

- *(bot)* Automatic tracking file TTL cleanup (v5.12.0)
## [5.11.1] - 2025-10-31

### 🐛 Bug Fixes

- *(bot)* Increase watchexec stop timeout to 10s (v5.11.1)
## [5.11.0] - 2025-10-31

### 🐛 Bug Fixes

- *(bot)* Atomic PID file locking with fcntl (v5.11.0)
## [5.10.0] - 2025-10-31

### 🚀 Features

- *(bot)* Persist content deduplication state across restarts (v5.10.0)
## [5.9.0] - 2025-10-31

### 🚀 Features

- *(bot)* Add comprehensive lifecycle management system (v5.6.0)
- *(bot)* Add full supervision chain with launchd + watchexec (v5.7.0)
- *(bot)* [**breaking**] Add rate limit protection and Pushover alerts (v5.9.0)

### 🐛 Bug Fixes

- *(bot)* Disable idle timeout for development mode
- *(lychee)* Extract user prompts from array-format transcript messages

### 🚜 Refactor

- *(lychee)* Archive and remove v3 notification dead code
- *(bot)* Remove development mode, production-only (v5.8.0)

### ⚡ Performance

- *(lychee)* Optimize transcript extraction to prevent hook timeouts

### ⚙️ Miscellaneous Tasks

- Complete dev mode cleanup and align shell config (v5.8.0)
- *(lychee)* Comprehensive cleanup - remove obsolete scripts and docs
## [5.5.1] - 2025-10-30

### 🚀 Features

- *(docs)* Add multi-layered bot startup enforcement
- *(bot)* Integrate notification system with watchexec

### 🐛 Bug Fixes

- *(lychee)* Strip whitespace from user_prompt before italic formatting
- *(lychee)* Replace newlines in user_prompt for italic formatting
- *(lychee)* Change session debug format to two lines
- *(bot)* Load doppler credentials for restart notifications
- *(lychee)* Fix MarkdownV2 backtick wrapping and user prompt rendering
- *(hook)* Extract actual user prompts, skip tool results

### 🚜 Refactor

- *(lychee)* Remove legacy bot starter from Stop hook

### 📚 Documentation

- *(lychee)* Add v5.4.0 to CHANGELOG
- *(lychee)* Add v5.5.0 to CHANGELOG for Stop hook refactoring
- *(lychee)* Add v5.5.1 to CHANGELOG for transcript extraction fix
## [5.4.0] - 2025-10-30

### 🚀 Features

- *(lychee)* Complete Phase 2 - migrate all messages to MarkdownV2

### 📚 Documentation

- *(lychee)* Update changelog and SSoT plan for v5.3.0
## [5.3.0] - 2025-10-30

### 🚀 Features

- *(lychee)* Add telegramify-markdown library (Phase 1 - MarkdownV2 support)

### 🐛 Bug Fixes

- *(lychee)* Fix session ID extraction (remove xargs for reliability)

### 🚜 Refactor

- *(lychee)* Simplify bot restart notifications (match system format)

### 📚 Documentation

- *(lychee)* Update changelog for v5.2.0
- Update SSoT plan with Phase 1 implementation findings
## [5.2.0] - 2025-10-30

### 🚀 Features

- *(lychee)* Migrate PID management to psutil (industry-standard)
## [5.1.1] - 2025-10-30

### 🐛 Bug Fixes

- *(bot)* Handle stale PID files during watchexec restarts
## [5.1.0] - 2025-10-30

### 🚀 Features

- *(telegram)* Add markdown-safe formatting utilities
- *(skills)* Add MQL5 indicator patterns skill
- *(monitoring)* Add dual-channel restart notifications
- *(monitoring)* Enhance restart notifications with detailed diagnostics
- *(skills)* Add dual-channel watchexec notification skill
- *(telegram)* Migrate all messages from Markdown to HTML parse mode

### 🐛 Bug Fixes

- *(orchestrator)* Initialize headless_session_id to prevent UnboundLocalError
- *(telegram)* Add fallback notification and fix markdown escaping
- *(telegram)* Handle duplicate message update errors gracefully
- *(monitoring)* Improve file detection and add message archiving
- *(notifications)* Fix MESSAGE variable expansion in heredoc
- *(notifications)* Remove markdown escaping for paths in backticks
- *(notifications)* Escape literal underscores in monitoring footer
- *(telegram)* Migrate notification system from Markdown to HTML parse mode

### 🚜 Refactor

- *(skills)* Make dual-channel-watchexec skill self-contained

### 📚 Documentation

- Add repository development guidelines
- Add Telegram message formatting specification

### 🎨 Styling

- *(changelog)* Standardize markdown formatting

### ⚙️ Miscellaneous Tasks

- Update changelog for v5.0.0
- Migrate stop hook from prettier to mdformat
## [5.0.0] - 2025-10-29

### 🚜 Refactor

- *(bot)* Extract async services to dedicated module (Phase 5)

### ⚙️ Miscellaneous Tasks

- Update changelog for v4.9.0
## [4.9.0] - 2025-10-29

### 🚜 Refactor

- *(bot)* Extract handler classes to dedicated module (Phase 4)

### 📚 Documentation

- Update SSoT plan with Phase 3 and final results
- Add Phase 4-5 deep dive analysis to SSoT plan

### ⚙️ Miscellaneous Tasks

- Update changelog for v4.8.0
## [4.8.0] - 2025-10-29

### 🚜 Refactor

- *(bot)* Extract handler functions to dedicated module (Phase 3)

### 📚 Documentation

- Update SSoT plan with Phase 2 findings

### ⚙️ Miscellaneous Tasks

- Update changelog for v4.7.0
## [4.7.0] - 2025-10-29

### 🚜 Refactor

- *(bot)* Extract file processors and progress tracking (Phase 2)

### 📚 Documentation

- Update SSoT plan with Phase 1 findings

### ⚙️ Miscellaneous Tasks

- Update changelog for v4.6.0
## [4.6.0] - 2025-10-29

### 🚜 Refactor

- *(bot)* Extract validators, formatters, keyboards to modules (Phase 1)
## [4.5.1] - 2025-10-29

### 🚀 Features

- *(telegram)* Preserve user prompt and assistant response context in workflow completion messages

### 🐛 Bug Fixes

- *(lychee)* Use bot_state.workflow_registry in summary handler
- *(lychee)* Detect lychee crashes and malformed output as errors
- *(telegram)* Escape markdown characters in workflow completion context

### 🚜 Refactor

- *(lychee)* Extract shared utilities and consolidate handler base class
- *(lychee)* Extract formatting and workflow utilities into dedicated modules
- *(lychee)* Extract bot state, utilities, and message builders into dedicated modules

### ⚙️ Miscellaneous Tasks

- *(todos)* Update CCI indicator task tracking for Strategy Tester phase
- *(todos)* Clear completed CCI indicator Strategy Tester session tasks
- Bump version to 4.5.1
## [4.5.0] - 2025-10-29

### 🚀 Features

- *(lychee)* Enhance workflow context display and session tracking

### 🐛 Bug Fixes

- *(lychee)* Align workspace tracking and improve workflow ID parsing
- *(lychee)* Use workspace_hash for progress tracking consistency

### 💼 Other

- Re-disable always-thinking mode
- Enable always-thinking mode
- Disable always-thinking mode
- *(lychee)* Add workspace tracking debug output and improve code organization

### 🚜 Refactor

- *(telegram)* Remove document attachments, use inline truncated messages
- *(lychee)* Improve progress tracking lifecycle and error handling

### 📚 Documentation

- *(lychee)* Release v4.5.0 - fix critical workspace ID mismatch bug

### ⚙️ Miscellaneous Tasks

- *(todos)* Update task tracking for CCI Neutrality indicator implementation
- *(todos)* Update CCI indicator task tracking for compilation phase
- *(todos)* Clear completed CCI indicator agent session tasks
## [4.4.0] - 2025-10-28

### 🚜 Refactor

- *(lychee)* Remove inject-results SessionStart hook
## [4.3.0] - 2025-10-28

### 🚜 Refactor

- *(telegram)* Migrate to AIORateLimiter for library-maintained rate limiting
## [4.2.0] - 2025-10-28

### 🚀 Features

- *(telegram)* Add git porcelain display and commit-changes workflow
- *(plugins)* Add skills-powerkit plugin and enable always-thinking mode
- *(skills)* Add MQL5 article extraction and Python workspace skills
- *(skills)* Add MLflow experiment tracking query skill
- *(skills)* Add MQL5 data ingestion research skill
- *(telegram)* Add single-message progress streaming specification
- *(telegram)* Implement single-message progress streaming for workflows
- *(telegram)* Enhance progress tracking with persistent git context
- *(telegram)* Add development and production runner scripts
- *(telegram)* Add launchd service manager and watchexec auto-reload
- *(telegram)* Add user prompt to SessionSummary messages
- *(telegram)* Compact git status format with persistent tracking

### 🐛 Bug Fixes

- *(prettier)* Use /private/tmp instead of /tmp for macOS symlink compatibility
- *(telegram)* Redirect orchestrator output to log file instead of pipes
- *(orchestrator)* Add missing SUMMARIES_DIR constant
- *(telegram)* Embed summary_data in WorkflowSelection to prevent race condition
- *(telegram)* Use uv run instead of python for dev script
- *(telegram)* Extract last Claude CLI response for SessionSummary title

### 💼 Other

- Disable always-thinking mode

### 📚 Documentation

- *(telegram)* Add docstring to template validator
- *(doc-intelligence)* Add comprehensive docstrings to tools
- *(telegram)* Add bot documentation with auto-reload guide
- *(skills)* Document official MQL5 docs extraction capability

### ⚙️ Miscellaneous Tasks

- *(submodule)* Update github-issues-skills to latest commit
- *(todos)* Update agent task list for config tracking
- *(submodule)* Update anthropic-agent-skills with documentation improvements
- *(todos)* Clear completed agent task list
## [4.1.0] - 2025-10-28

### 🚀 Features

- *(telegram)* Add WorkflowExecution completion messages
## [backup-before-telegram-merge] - 2025-10-28

### 🚀 Features

- Add Haiku-powered auto-commit for prettier hook

### 🐛 Bug Fixes

- *(cleanup)* Handle sourcing in non-BASH_SOURCE environments
- *(skills)* Standardize chezmoi-workflows YAML frontmatter
- *(skills)* Standardize doppler-workflows YAML frontmatter
- *(skills)* Standardize all latex skill YAML frontmatter
- *(skills)* Standardize python and troubleshooting skill YAML frontmatter
- *(telegram)* Make all workflows show consistently across workspaces
- *(telegram)* Make all workflows show consistently across workspaces
- *(settings)* Switch to custom statusline script

### 🚜 Refactor

- *(skills)* Split code-clone-assistant for token efficiency

### 📚 Documentation

- Add GitHub issue draft and code-clone-assistant skill
- *(specs)* Update SSoT with phase-1 outcomes
- *(specs)* Update SSoT to v1.2.0 - phase 2 complete

### ⚙️ Miscellaneous Tasks

- Add lock file patterns to .gitignore
## [0.3.0-single-instance-protection] - 2025-10-27

### 🚀 Features

- Implement single-instance protection system

### 📚 Documentation

- Add comprehensive hook testing recommendations
## [0.2.1-cns-output-fix] - 2025-10-27

### 🐛 Bug Fixes

- *(cns)* Add output redirection to all CNS hook background processes
## [0.2.0-stop-hook-error-fixed] - 2025-10-27

### 🚀 Features

- *(telegram)* Implement P1 rate limiting and markdown safety
- *(telegram)* Implement P2 streaming progress updates

### 🐛 Bug Fixes

- *(v4)* Strip newlines from wc output to prevent malformed JSON
- *(v4)* Prevent double-zero in JSON by using grep || true
- *(v4)* Shorten workflow button names for Telegram display
- *(v4)* Support all workspaces with fallback for unregistered ones
- *(lychee)* Add workspace fallback to CompletionHandler
- *(lychee)* Invoke orchestrator when workflow button clicked
- *(lychee)* Add workspace fallback to button confirmation messages
- *(lychee)* Add extensive logging to progress poller and improve schema.json filtering
- *(lychee)* Suppress uv debug output in hook to prevent false error in Claude Code CLI
- *(lychee)* Suppress event_logger stdout to prevent hook error in Claude Code CLI
- *(cns)* Add missing exit 0 to prevent hook output
- *(hooks)* Add block-level output redirection to all background processes

### 💼 Other

- *(lychee)* Increase timeouts from 5/10min to 30min

### 🚜 Refactor

- *(lychee)* Disable v3 notification emission (prevents duplicates)

### 📚 Documentation

- *(lychee)* Add implementation plan for P1/P2 telegram improvements
- *(telegram)* Update SSoT with P1 findings and completion status
- *(telegram)* Update SSoT with P2 completion (commit 0dab467)

### ⚙️ Miscellaneous Tasks

- Ignore agent todo files in todos/ directory
- *(lychee)* Consolidate telegram files and fix logging paths
## [4.0.0] - 2025-10-26

### 🚀 Features

- *(telegram-workflows)* Add v4.0.0 architecture specification and migration plan
- *(v4)* Apply pre-migration fixes for v3.0.1→v4.0.0
- *(v4)* Establish v3.0.1 baseline and archive verification docs
- *(v4)* Complete Phase 0 pre-migration validation
- *(v4)* Complete Phase 1 - create workflow registry
- *(v4)* Implement Phase 2 - hook emits session summaries with git status and duration
- *(v4)* Implement Phase 3 - bot refactor with workflow menu system
- *(v4)* Implement Phase 4 - orchestrator with multi-workflow execution and Jinja2 templates

### 💼 Other

- *(v4)* Phase 4 scaffolding - orchestrator infrastructure

### 🚜 Refactor

- Remove slash commands in favor of plugin system

### 📚 Documentation

- *(lychee)* Update lifecycle analysis and workflow docs to v3.0.1
- *(migration)* Add critical audit of v4.0.0 migration plan
- *(v4)* Update SSoT with Phase 0-1 completion and continuation plan
- *(v4)* Finalize v4.0.0 release documentation

### ⚙️ Miscellaneous Tasks

- Update .gitignore and add architecture docs
- Add remaining workspace baseline files
- Update session state and SSoT formatting
- *(skills)* Rename skill-builder to agent-skill-builder
## [pruning-baseline-2025-10-25] - 2025-10-23

### 🚀 Features

- *(automation)* Add Prettier markdown formatting Stop hook

### 🎨 Styling

- Format markdown files with Prettier

### ⚙️ Miscellaneous Tasks

- Bump version to 2.2.0
## [2.1.0] - 2025-10-22

### 🚀 Features

- *(shells,zellij)* Configure Zellij session recovery in zsh
- *(skills)* [**breaking**] Implement hierarchical global skills architecture

### 📚 Documentation

- Update CHANGELOG and RELEASE_NOTES for v2.9.0
- *(memory)* Optimize context consumption via progressive disclosure
- Update CHANGELOG and RELEASE_NOTES for v2.9.0
- Update repository references from Eon-Labs to terrylica
- *(audit)* Exhaustive documentation audit and consistency fixes
- *(ssh)* Analyze caching issue and document solutions for next session
- *(zellij)* Add balanced power-user configuration and comprehensive historical tracking guide
- *(zellij)* Document Shift+Click workaround for hyperlink clicking
- *(zellij)* Document macOS-specific Shift+Cmd+Click for links

### ⚙️ Miscellaneous Tasks

- Update session tracking
## [2.9.0] - 2025-10-13

### 🚀 Features

- *(development)* Integrate comprehensive tmux workspace management system
- *(monitoring)* Capture comprehensive session analytics with extended followup trigger data
- *(sessions)* Organize session data structure and agent todo system management
- *(tooling)* Implement GitHub Flavored Markdown link checker with user memory updates
- *(monitoring)* Capture GitHub Flavored Markdown link checker session analytics
- *(agents)* Create `research-scout` agent with comprehensive research direction generation
- *(tts)* Implement Phase 1 modular TTS foundation with comprehensive architecture
- *(commands)* Implement comprehensive APCF slash command documentation
- *(gfm-checker)* Implement comprehensive short flag compatibility for command-line interface
- *(commands)* Implement comprehensive command validation infrastructure with auto-fix capabilities
- *(tts)* Implement separated content-type processing with JSON-driven configuration management
- *(tts)* Implement intelligent command detection with content-type differentiation for enhanced audio feedback
- *(tts)* Implement ultra-aggressive content filtering with dual-mode clipboard integration
- *(hooks)* Implement automated conversation export system with claude-code-exporter integration
- *(cns)* Expand documentation architecture and enhance Mac IIx sound notification system
- *(tools)* Implement automated Python code quality system with ruff integration
- *(cns)* Update notification sound from Mac IIx to Toy Story audio
- *(cns)* Optimize audio timing and enhance dot-folder pronunciation
- *(cns)* Add configurable volume control for notification audio
- *(infrastructure)* Establish organizational repository foundation with migration audit trail
- *(gfm-checker)* Implement README completeness validation with workspace navigation repairs
- *(utilities)* Implement direct execution utilities with structured documentation framework
- *(link-checker)* Implement sub-repository ignore functionality with case-insensitive pattern matching
- *(tools)* Implement SAGE development productivity tool with comprehensive alias system
- *(sync)* Implement comprehensive SAGE dual-environment synchronization tool with error handling and validation
- *(commands)* Implement command extension documentation consolidation with workflow integration
- *(agents)* Implement Python import validation agent with comprehensive static analysis pipeline
- *(automation)* Implement comprehensive CNS notification system with asynchronous hook architecture
- *(tools)* Implement GitHub Flavored Markdown link integrity validation with intelligent auto-fix
- *(qa)* Implement comprehensive command validation and Python code quality automation tools
- *(infrastructure)* Implement SAGE development aliases with universal access pattern and dual-environment workflow integration
- *(infrastructure)* Implement bulletproof SAGE sync v2.0 with emergency backup system
- *(architecture)* Implement CAAP framework with comprehensive agent standards
- *(consolidation)* Implement Python QA consolidation with unified quality assurance
- *(enhancement)* Implement sophisticated research-scout with multi-perspective analysis
- *(architecture)* Implement CAAP-compliant APCF agent with command delegation
- *(tools)* Add Claude session sync utility for cross-platform session management
- *(sync)* Implement bidirectional sync with official session format
- *(tmux)* Add smart detach command with session auto-detection EL-1009
- *(EPMS)* Add Universal Workspace Integration principles
- *(fdap)* Add Fail-Fast Data Authenticity Precept to user memory
- *(uv)* Enforce module-only execution pattern
- Integrate comprehensive workspace system improvements
- Add comprehensive quantitative development standards and CCXT mandate
- Consolidate quantitative development standards after c9c968a merge
- Implement zero-tolerance temporal integrity mandate for quantitative finance
- Add agent todo management system and workspace sync capability
- Add context-bound-planner agent with todo state sync
- Implement CNS Remote Alert System with hybrid SSH tunnel architecture
- CNS Remote Alert System production implementation
- Pushover notification integration with emergency retry system
- *(tools)* Add git-cliff release automation templates and AI agent workflow
- *(cns)* Complete Pushover integration with git-based credentials
- *(cns)* Enable dual SSH tunnel and Pushover notifications
- *(cns)* Add configurable Pushover notification sound
- Enable Claude Code session history tracking
- *(hooks,docs)* Add session ID display and ccstatusline integration

### 🐛 Bug Fixes

- *(hooks)* Update settings.json paths after automation script reorganization
- *(tts)* Correct automation script path after directory reorganization
- *(tts)* Resolve clipboard debug functionality for user content capture and refine command detection accuracy
- *(tts)* Enhance slash command detection and clipboard filtering for command workflows
- *(command-interface)* Resolve flag completeness gap with comprehensive wrapper synchronization
- *(sage)* Update hardcoded paths after directory restructure

### 💼 Other

- *(attribution)* Disable automatic Claude attribution in commit messages
- *(documentation)* Reorganize tool usage preferences in Claude Code user memory
- *(httpx)* Optimize GFM link checker dependencies with modern HTTP client
- *(gfm-checker)* Modernize Python dependency management with \`httpx\` optimization
- *(ide)* Implement comprehensive basedpyright/pyright disabler for Cursor IDE development environment
- *(cns)* Implement configurable clipboard control mechanism
- *(claude)* Restructure principle hierarchy for workspace-wide evolutionary development application
- *(workspace)* Establish working directory preservation principle with universal path construction enforcement
- *(infrastructure)* Establish universal access shell integration with working directory preservation
- *(architecture)* Refine universal access principles with dependency management consolidation
- *(architecture)* Implement hybrid tool access architecture with industry standard ~/.local/bin pattern
- *(system)* Investigate Claude Code workspace configuration optimization
- *(infrastructure)* Implement universal tool installation system with cross-platform automation
- *(infrastructure)* Implement SAGE sync command with workspace synchronization capabilities
- Pre-MHR modularization state for rollback reference
- Merge conflicts by accepting remote changes after sync
- Remove obsolete statsig and todos directories
- Branch rename planning todos
- Branch rename completion progress
- Add comprehensive documentation audit milestone log
- Add Python-Rust integration and session tracking milestone log
- Add comprehensive quantitative development standards milestone log
- Add extension specification externalization milestone log
- Add temporal integrity mandate milestone log
- Add agent session handoff continuity milestone log
- Add agent todo management system milestone log
- Sync todo state for agent b12461b7
- Sync todo state for milestone log generation
- Add context-bound-planner agent ecosystem milestone log
- Sync agent todo states with session continuity
- Add agent todo state synchronization milestone log
- Add CNS Remote Alert System milestone log
- CNS Remote Alert System comprehensive plan with audio preservation
- Milestone log creation task status for CNS Remote Alert System
- Update CNS Remote Alert System production implementation log
- CNS remote client and hook entry refinements
- CNS Remote Alert System Linux-side completion and production validation
- Workspace evolutionary compliance cleanup documentation
- CNS remote client and hook entry refinements
- Sync todo state changes
- Milestone creation task status update
- CNS Remote Alert System refinements and enhanced reliability
- Add Pushover notification integration system log for commit 0dd6e4d
- User memory and todo state synchronization
- Add user memory and todo state synchronization log for commit 924cb84
- Version evolution and todo state synchronization
- Disk space recovery and documentation intelligence system
- Add workspace optimization and documentation intelligence log for commit 02e1dba
- Sessions directory structure and exported conversation log
- User memory architecture optimization with machine-readable specification externalization
- User memory architecture optimization with 84% reduction and specification externalization
- Claude code cli configuration enhancements with model selection and status line integration
- Claude code cli configuration enhancements for commit c0bfb40
- Fallback-removal-validator agent with pattern-matching infrastructure
- Comprehensive agent ecosystem cleanup and optimization
- Initialize Commitizen configuration
- Version 2.0.0 → 2.1.0
- Version 2.1.0 → 2.2.0
- Version 2.2.0 → 2.3.0
- Version 2.3.0 → 2.4.0
- Version 2.4.0 → 2.5.0
- Version 2.5.0 → 2.6.0
- Version 2.6.0 → 2.7.0
- Version 2.7.0 → 2.8.0
- Version 2.7.0 → 2.8.0
- Version 2.8.0 → 2.9.0

### 🚜 Refactor

- *(architecture)* Implement hierarchical configuration management system
- *(structure)* Rename scripts directory to tools for clarity
- *(automation)* Organize scripts into logical subdirectories
- *(agents)* Standardize all agent configurations to consistent YAML frontmatter template
- *(config)* Streamline APCF documentation in user memory file
- *(tts)* Simplify clipboard functionality to preserve raw conversation content
- *(tts)* Remove TTS functionality and implement clipboard-only system with glass sound
- Complete TTS to CNS rename - eliminate misleading terminology across entire system
- *(cns)* Eliminate TTS legacy contamination and optimize workspace architecture
- *(automation)* Eliminate non-CNS hook system and consolidate to pure CNS architecture
- *(automation)* Implement cross-platform compatibility for CNS system
- *(tmux)* Eliminate complex automation and implement simple session management
- *(agents)* Optimize agent definitions through complexity reduction investigation
- *(docs)* Systematic documentation architecture optimization for maintainability
- *(integration)* Consolidate cross-platform system integration documentation
- *(tools)* Implement development tool integration research with documentation consolidation
- *(workspace)* Implement systematic workspace organization with documentation consolidation architecture
- *(agents)* Migrate to official Claude Code agent directory structure
- *(commands)* Streamline APCF command for CAAP delegation efficiency
- *(agents)* Restructure agent system and workspace configuration EL-1009
- *(exception-only)* Implement strict exception-only failure principles across workspace
- *(agents)* Update milestone-commit-logger for workplace agnosticism
- *(agents)* Rename mhr-refactor to workspace-refactor
- Externalize extension specifications to YAML files
- Implement agent session handoff with todo list continuity

### 📚 Documentation

- *(infrastructure)* Establish comprehensive configuration documentation and protective measures
- *(readme)* Fix broken links and add missing documentation files
- *(sessions)* Add project memory documentation for cross-session context
- Update references to renamed tools directory
- Add comprehensive directory documentation and Claude Code file safety guide
- Add Claude Code official file warnings to main documentation
- Update system architecture for current directory structure
- Comprehensive accuracy audit and system architecture updates
- *(memory)* Update TTS system documentation for modular architecture transition
- *(architecture)* Synchronize documentation with modular TTS foundation implementation
- *(config)* Modernize Python library preferences in user memory
- *(gfm-check)* Synchronize command documentation with implemented flag behavior
- Update all documentation for TTS removal and clipboard-only system
- Finalize CNS documentation updates and hook path corrections
- *(workspace)* Update ARCHITECTURE.md v2.2 - comprehensive workspace modernization
- *(cns)* Eliminate glass sound legacy terminology across workspace architecture
- *(workspace)* Update documentation for portable architecture and simplified workflows
- *(apcf)* Enhance command documentation with execution best practices
- *(claude)* Enhance documentation structure with planning methodology principles
- *(readme)* Optimize root documentation for new Claude Code user onboarding
- *(workspace)* Implement evolutionary language principles with categorized documentation structure
- *(readme)* Establish repository identity as Claude Code global configuration template
- *(cleanup)* Remove legacy migration documentation and correct CNS clipboard status
- *(tooling)* Implement universal workspace access for GFM link checker cross-platform tooling
- *(consolidation)* Establish repository identity with legacy documentation cleanup
- *(apcf)* Refine authenticity template to eliminate timestamp redundancy with unique developer insight focus
- *(workflow)* Establish dual-environment synchronization strategy with comprehensive setup documentation
- *(architecture)* Establish consolidated documentation structure with GitHub rendering compatibility
- Add workspace overview documentation with agent directory structure
- *(config)* Add module housekeep refactoring methodology with import stability guardrails
- *(methodology)* Add standalone APCF commit format reference with SR&ED evidence generation
- *(agents)* Implement comprehensive agent documentation system with APCF gitignore conflict detection
- *(standards)* Add verified Claude session storage standard; reorganize docs structure and fix links
- *(standards)* Add recovery/troubleshooting; add session-recovery.sh; remove legacy projects symlink EL-1009
- *(sync)* Update command documentation for bidirectional sync capability
- *(architecture)* Add session storage standards and reorganize docs structure
- Add comprehensive milestone log for workspace system integration
- Comprehensive documentation audit and workspace hygiene improvements
- Add GPT-5 research integration and secure sudo helper
- Add Python-Rust integration toolchain and session state tracking
- Add CNS Remote Alert System Linux completion milestone log
- Workspace evolutionary compliance cleanup
- Expand toolchain preferences with PDF processing and Python package guidelines
- Standardize Python build toolchain with uv and hatchling
- Consolidate documentation and add git-cliff comprehensive workflow
- *(pushover)* Add emergency priority specification and implementation
- *(credentials)* Migrate Pushover credentials to Doppler
- *(terminal)* Add Ghostty terminal setup guide and enable session tracking
- Update PyPI token management to use Doppler
- Clarify Doppler as exclusive PyPI publishing method
- Add Kitty terminal configuration and session tracking
- Add SSH clipboard integration via OSC 52

### ⚡ Performance

- *(cns)* Implement asynchronous hook architecture to eliminate session delays

### ⚙️ Miscellaneous Tasks

- *(cleanup)* Remove unused audio assets and correct documentation references
- *(artifacts)* Archive development shell snapshots from extended session workflow
- *(artifacts)* Archive comprehensive zsh development environment snapshot
- *(config)* Optimize repository tracking strategy with runtime data exclusion
- *(hooks)* Remove followup.log from version control tracking
- *(commands)* Remove deprecated hub command documentation files
- *(system)* Remove deprecated IDE lock file from workspace cleanup
- *(workspace)* Add manual glass sound utility and improve gitignore patterns
- *(gitignore)* Resolve tracking conflicts with ignore patterns
- *(maintenance)* Consolidate legacy tooling with enhanced agent deployment
- *(cleanup)* Resolve root workspace clutter with strategic cleanup
- *(git)* Resolve gitignore conflict with emergency backup preservation
- *(housekeeping)* Enhance gitignore for comprehensive repository cleanup
- *(cleanup)* Archive legacy session system components
- Update session artifacts and agent state
- Update session artifacts and documentation
- Clean up session artifacts and IDE lock files
- Disable always thinking mode
- Update release notes and restore thinking mode
- Enable Claude Code session history tracking
- Preserve session history and update file path conventions

### 🛡️ Security

- Rust code quality enforcement and PyPI publishing best practices
- Add Rust code quality enforcement and PyPI publishing upgrade log for commit 3e81e83
- Version evolution and todo state synchronization for commit 23ad3a5
