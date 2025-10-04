
## 2.2.0 - 2025-10-04


### ✨ New Features

- Complete Pushover integration with git-based credentials Add automatic Pushover notifications to CNS with rich session metadata and git-based credential sharing for zero-setup team deployment. Features: - Dual notifications: local audio (afplay + say) + Pushover API - Session metadata: username@hostname, folder, session_id, hook_event - Git-based credentials in cns_config.json (team-shared, private repo) - Credential priority: CNS config → ~/.pushover_config → keychain - Cross-platform: macOS (audio + Pushover), Linux (Pushover only) - New tools: cns-setup-remote-pushover, cns-tunnel-listener, cns-diagnose Changes: - conversation_handler.sh: Add Pushover notification (262 lines, +56) - cns_hook_entry.sh: Export session metadata for remote client - cns_config.json: Add pushover credentials section - cns-remote-client.sh: Add session metadata to notifications - pushover-notify: Add git-based credential loading Documentation: - Update CNS README: Pushover integration, session metadata, deployment - Update specifications: CNS v2.0.0, Pushover credential priority - Update DEMO.md: CNS automatic notifications, credential sources Cleanup: - Remove deprecated scripts (8 files) - Remove legacy cns-unified directory (19 files) - Update .gitignore: CNS logs, test temp files Breaking changes: - CNS now sends Pushover notifications (requires credentials in config) - Removed cns-setup-remote-pushover requirement (git-based credentials)



### 📝 Other Changes

- Version 2.0.0 → 2.1.0

- 🛡️ Implement Universal .sessions Protection System PROTECTION MECHANISMS: • Hidden .sessions/ directory (dotfile convention) • .gitignore: Force track despite global ignore patterns • Pre-commit hook: Block deletion attempts • Auto-recovery script: .sessions/protect_sessions.sh • Force git tracking: All conversation history preserved UNIVERSAL COMPATIBILITY: Works for new workspaces or migrates existing sessions/ folders. All Claude Code conversation history permanently protected.

- Version 2.1.0 → 2.2.0



---
**Full Changelog**: https://github.com/Eon-Labs/rangebar/compare/v2.1.0...v2.2.0
