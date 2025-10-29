## [4.8.0] - 2025-10-29

### 🚜 Refactor

- *(bot)* Extract handler functions to dedicated module (Phase 3)

### ⚙️ Miscellaneous Tasks

- Update changelog for v4.7.0
## [4.7.0] - 2025-10-29

### 🚜 Refactor

- *(bot)* Extract file processors and progress tracking (Phase 2)

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

- Bump version to 4.5.1
## [4.5.0] - 2025-10-29

### 🚀 Features

- *(lychee)* Enhance workflow context display and session tracking

### 🐛 Bug Fixes

- *(lychee)* Align workspace tracking and improve workflow ID parsing
- *(lychee)* Use workspace_hash for progress tracking consistency

### 💼 Other

- *(lychee)* Add workspace tracking debug output and improve code organization

### 🚜 Refactor

- *(telegram)* Remove document attachments, use inline truncated messages
- *(lychee)* Improve progress tracking lifecycle and error handling

### 📚 Documentation

- *(lychee)* Release v4.5.0 - fix critical workspace ID mismatch bug
## [4.4.0] - 2025-10-28

### 🚜 Refactor

- *(lychee)* Remove inject-results SessionStart hook
## [4.3.0] - 2025-10-28

### 🚜 Refactor

- *(telegram)* Migrate to AIORateLimiter for library-maintained rate limiting
## [4.2.0] - 2025-10-28

### 🚀 Features

- *(telegram)* Add git porcelain display and commit-changes workflow
- *(telegram)* Implement single-message progress streaming for workflows
- *(telegram)* Enhance progress tracking with persistent git context
- *(telegram)* Add development and production runner scripts
- *(telegram)* Add launchd service manager and watchexec auto-reload
- *(telegram)* Add user prompt to SessionSummary messages
- *(telegram)* Compact git status format with persistent tracking

### 🐛 Bug Fixes

- *(telegram)* Redirect orchestrator output to log file instead of pipes
- *(orchestrator)* Add missing SUMMARIES_DIR constant
- *(telegram)* Embed summary_data in WorkflowSelection to prevent race condition
- *(telegram)* Use uv run instead of python for dev script
- *(telegram)* Extract last Claude CLI response for SessionSummary title

### 📚 Documentation

- *(telegram)* Add docstring to template validator
- *(telegram)* Add bot documentation with auto-reload guide
## [4.1.0] - 2025-10-28

### 🚀 Features

- Add Haiku-powered auto-commit for prettier hook
- *(telegram)* Add WorkflowExecution completion messages

### 🐛 Bug Fixes

- *(telegram)* Make all workflows show consistently across workspaces
- *(telegram)* Make all workflows show consistently across workspaces

### 📚 Documentation

- Add GitHub issue draft and code-clone-assistant skill
## [0.3.0-single-instance-protection] - 2025-10-27

### 🚀 Features

- Implement single-instance protection system
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

- Update session state and SSoT formatting
