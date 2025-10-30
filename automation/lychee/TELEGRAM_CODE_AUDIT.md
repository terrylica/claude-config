# Telegram Code Audit - Complete Inventory

**Date**: 2025-10-27
**Purpose**: Identify all Telegram-related code, specifications, and potential cleanup targets

---

## Executive Summary

**Status**: Code is reasonably well-organized with clear consolidation opportunities

**Key Findings**:

1. ✅ **Active runtime code properly consolidated** in `automation/lychee/runtime/`
1. ⚠️ **Specifications scattered** between global `/specifications/` and `automation/lychee/specifications/`
1. ⚠️ **Logs scattered** in global `/logs/` instead of `automation/lychee/logs/`
1. ✅ **Archive properly organized** - deprecated code clearly separated
1. ⚠️ **Markdown documentation duplicated** - TELEGRAM_IMPROVEMENTS_PLAN.md superseded by YAML spec

---

## 1. Active Runtime Code (Properly Organized)

### `/Users/terryli/.claude/automation/lychee/runtime/`

#### Bot

- `bot/multi-workspace-bot.py` - Main bot (v4.0.0 with P1+P2 features)
- `bot/multi-workspace-bot.py.backup` - Backup from pre-P1 implementation

#### Libraries

- `lib/telegram_helpers.py` - Safe wrappers (P1: rate limiting + markdown safety)
- `lib/test_telegram_helpers.py` - Unit tests (9/9 passing)
- `lib/workspace_helpers.py` - Workspace registry helpers (imported by bot)
- `lib/event_logger.py` - Event logging (imported by bot/orchestrator)
- `lib/ulid_gen.py` - Correlation ID generation

#### Orchestrator

- `orchestrator/multi-workspace-orchestrator.py` - Workflow orchestration (P2: progress emission)

#### Hooks

- `hook/check-links-hybrid.sh` - SessionStop hook (emits summaries → triggers bot)

**Status**: ✅ Well-organized, no cleanup needed

---

## 2. Specifications (SCATTERED - CONSOLIDATION NEEDED)

### Global Specifications (`/Users/terryli/.claude/specifications/`)

```
telegram-workflows-orchestration-v4.yaml       (30KB, Oct 26)
telegram-notification-progressive-disclosure.yaml (30KB, Oct 25)
```

**Issue**: These are Lychee-specific but stored globally

### Lychee Specifications (`/Users/terryli/.claude/automation/lychee/specifications/`)

```
telegram-bot-improvements.yaml                 (NEW, v1.1.0, P1+P2 SSoT)
```

**Recommendation**:

- ✅ Keep `telegram-bot-improvements.yaml` in `automation/lychee/specifications/`
- ⚠️ **MOVE** the two global YAML specs into `automation/lychee/specifications/`
- Update all references in code/docs

---

## 3. State Files (Active)

### `/Users/terryli/.claude/automation/lychee/state/`

```
telegram_session.session                       (Pyrogram auth session)
bot.pid                                        (Current bot PID)
progress/schema.json                           (P2: ProgressUpdate schema)
workflows.json                                 (Workflow registry)
registry.json                                  (Workspace registry)
events.db                                      (SQLite event store)
```

**Status**: ✅ Properly located, no cleanup needed

---

## 4. Setup Scripts (Active)

### `/Users/terryli/.claude/automation/lychee/setup/`

#### Authentication

- `auth/auth-telegram.py` - Interactive Telegram authentication
- `auth/auth-telegram-noninteractive.py` - Headless authentication

#### Bot Setup

- `bot/create-bot-automated.py` - Bot creation automation

**Status**: ✅ Properly organized

---

## 5. Logs (SCATTERED - CONSOLIDATION NEEDED)

### Global Logs (`/Users/terryli/.claude/logs/`)

```
telegram-handler.log                           (9KB, Oct 26)
telegram-handler.error.log                     (1.9MB, Oct 24)
```

**Issue**: Lychee logs stored globally instead of in `automation/lychee/logs/`

**Recommendation**:

- ⚠️ **CREATE** `automation/lychee/logs/` directory
- ⚠️ **MOVE** telegram logs from global `/logs/` to `automation/lychee/logs/`
- Update bot logging configuration

---

## 6. Archive (Properly Organized)

### `/Users/terryli/.claude/automation/lychee/archive/`

#### Deprecated Code

- `deprecated-code/webhook/telegram-webhook-handler.py` - Old webhook approach (replaced by polling)

#### Version Archive

- `v2.1.0/com.user.lychee.telegram-handler.plist` - Old launchd config

**Status**: ✅ Properly archived, no cleanup needed

---

## 7. Documentation (DUPLICATION - CLEANUP NEEDED)

### Markdown Files

```
automation/lychee/TELEGRAM_IMPROVEMENTS_PLAN.md    (Superseded by YAML spec)
automation/lychee/MIGRATION_v3_to_v4_PLAN_v2.md    (References telegram workflows)
automation/lychee/MIGRATION_COMPLETE.md            (Migration status)
automation/lychee/PHASE_4_HANDOFF.md               (Phase 4 plan)
automation/lychee/RELEASE_NOTES_v4.0.0.md          (v4.0.0 release notes)
automation/lychee/tests/INTEGRATION_TESTS.md       (Test documentation)
automation/lychee/docs/COMPLETE_WORKFLOW.md        (Workflow documentation)
automation/lychee/docs/DEPLOYMENT.md               (Deployment guide)
automation/lychee/docs/QUICK_START.md              (Quick start)
automation/lychee/README.md                        (Main README)
```

**Issue**: `TELEGRAM_IMPROVEMENTS_PLAN.md` duplicates information now in `telegram-bot-improvements.yaml`

**Recommendation**:

- ⚠️ **PRUNE** `TELEGRAM_IMPROVEMENTS_PLAN.md` - superseded by SSoT YAML spec
- Update it to reference `specifications/telegram-bot-improvements.yaml` instead

---

## 8. Testing

### `/Users/terryli/.claude/automation/lychee/testing/`

```
test-notification-emit.py                      (Notification emission test)
test-headless-invocation.py                    (Headless test)
inject-results.sh                              (Result injection)
```

**Status**: ✅ Properly organized

---

## 9. Configuration

### Launchd

- `config/launchd/` - Empty or minimal (bot runs on-demand, not as daemon)

### Zellij

- `config/zellij/` - Terminal multiplexer config

**Status**: ✅ No telegram-specific config issues

---

## Consolidation Plan

### HIGH PRIORITY

1. **Move global specifications to lychee**

   ```bash
   mv /Users/terryli/.claude/specifications/telegram-*.yaml \
      /Users/terryli/.claude/automation/lychee/specifications/
   ```

1. **Prune superseded markdown**
   - Update `TELEGRAM_IMPROVEMENTS_PLAN.md` to reference SSoT YAML
   - Or delete if fully superseded

1. **Consolidate logs**

   ```bash
   mkdir -p /Users/terryli/.claude/automation/lychee/logs
   mv /Users/terryli/.claude/logs/telegram-*.log \
      /Users/terryli/.claude/automation/lychee/logs/
   ```

### MEDIUM PRIORITY

4. **Update bot logging paths**
   - Change log file paths in bot to use `automation/lychee/logs/`

1. **Remove backup file**
   - Delete `multi-workspace-bot.py.backup` after confirming P1+P2 stability

### LOW PRIORITY

6. **Verify archive completeness**
   - Confirm no active code accidentally in `archive/`

---

## Outside Lychee Folder

### Global Areas with Telegram References

1. **`/Users/terryli/.claude/specifications/`** (2 YAML files) - MOVE to lychee
1. **`/Users/terryli/.claude/logs/`** (2 log files) - MOVE to lychee
1. **`/Users/terryli/.claude/docs/architecture/`** - General architecture docs (mentions telegram in task queue context)

**Status**: Only specifications and logs need consolidation

---

## Dangling/Forgotten Components

### Analysis

✅ **No dangling components found** - All code is either:

- Active and properly located in `automation/lychee/runtime/`
- Archived in `automation/lychee/archive/`
- Setup scripts in `automation/lychee/setup/`

⚠️ **Minor organization issues**:

1. Specifications split between global and lychee
1. Logs in global `/logs/` instead of lychee
1. Markdown docs duplicate YAML specs

---

## Implementation Checklist

**Phase 1: Consolidation** (safe, no code changes)

- [ ] Create `automation/lychee/logs/` directory
- [ ] Move 2 YAML specs from global to lychee
- [ ] Move 2 log files from global to lychee
- [ ] Update SSoT references in code/docs

**Phase 2: Documentation** (safe)

- [ ] Update `TELEGRAM_IMPROVEMENTS_PLAN.md` to reference YAML SSoT
- [ ] Update README with correct spec locations

**Phase 3: Code Updates** (requires testing)

- [ ] Update bot log paths to `automation/lychee/logs/`
- [ ] Test bot restart with new paths

**Phase 4: Cleanup** (after verification)

- [ ] Remove `multi-workspace-bot.py.backup`
- [ ] Prune outdated markdown docs if fully superseded

---

## Conclusion

**Overall Status**: ✅ Code is well-organized with minor consolidation opportunities

**No Dangling Code**: All telegram code is accounted for and properly located

**Recommended Actions**:

1. Consolidate specifications into lychee folder
1. Consolidate logs into lychee folder
1. Update markdown docs to reference YAML SSoT
1. Minor path updates in bot configuration

**Risk**: Low - All changes are organizational, no logic changes required
