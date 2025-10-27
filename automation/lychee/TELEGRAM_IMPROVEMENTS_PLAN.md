# Telegram Bot Improvements - Implementation Plan

**Date**: 2025-10-27
**Priority**: P1 (Rate Limiting + Markdown Safety), P2 (Streaming Updates)
**Goal**: Prevent bot bans, improve UX, maintain stability

---

## Regression Prevention Strategy

### Pre-Implementation Checklist
- [x] All existing fixes committed and pushed (5 commits)
- [x] Bot running successfully (PID: 76698)
- [x] Existing workflows validated (fix-docstrings, prune-legacy, etc.)
- [ ] Backup current working bot.py
- [ ] Create feature branch for improvements
- [ ] Test each change incrementally

### Rollback Plan
- Git revert to commit `9c29506` if issues detected
- Bot restart procedure documented
- State files preserved (no schema changes)

---

## Priority 1: Rate Limiting & Markdown Safety

### Problem Statement
1. **Rate Limiting**: Telegram API limits message edits to 6/second
   - 429 errors can result in temporary bot ban
   - No current handling of RetryAfter errors

2. **Markdown Safety**: Raw text without validation
   - Unclosed markdown tags cause "can't parse entities" errors
   - Streaming responses can split markdown tokens

### Impact Analysis
**Affected Locations** (8 total):
```
NotificationHandler.send_notification()     → send_message (line 380)
CompletionHandler.send_completion()         → send_message (line 477)
SummaryHandler.send_workflow_menu()         → send_message (line 741)
handle_workflow_selection()                 → edit_message_text (lines 990, 1067, 1076)
handle_callback()                           → edit_message_text (lines 1105, 1190)
```

### Implementation Steps

#### Step 1: Create Helper Module
**File**: `/Users/terryli/.claude/automation/lychee/runtime/lib/telegram_helpers.py`

**Functions**:
```python
async def safe_edit_message(
    query,
    text: str,
    parse_mode: str = "Markdown",
    max_retries: int = 3
) -> bool:
    """
    Edit message with rate limit handling and markdown safety.

    Returns:
        True if successful, False if failed after retries
    """
    # 1. Validate and fix markdown
    safe_text = ensure_valid_markdown(text)

    # 2. Try edit with exponential backoff
    retry_count = 0
    while retry_count < max_retries:
        try:
            await query.edit_message_text(safe_text, parse_mode=parse_mode)
            return True
        except telegram.error.RetryAfter as e:
            wait_time = e.retry_after
            print(f"⚠️  Rate limit: waiting {wait_time}s")
            await asyncio.sleep(wait_time)
            retry_count += 1
        except telegram.error.TelegramError as e:
            if "429" in str(e):
                wait_time = 2 ** retry_count  # Exponential backoff
                print(f"⚠️  Rate limit (429): backing off {wait_time}s")
                await asyncio.sleep(wait_time)
                retry_count += 1
            else:
                # Other errors - log and re-raise
                print(f"❌ Telegram error: {e}")
                raise

    print(f"❌ Failed to edit message after {max_retries} retries")
    return False


async def safe_send_message(
    bot,
    chat_id: int,
    text: str,
    parse_mode: str = "Markdown",
    max_retries: int = 3,
    **kwargs
):
    """Send message with rate limit handling and markdown safety"""
    safe_text = ensure_valid_markdown(text)

    # Similar retry logic as safe_edit_message
    # ... (implementation)


def ensure_valid_markdown(text: str) -> str:
    """
    Close unclosed markdown tags to prevent parse errors.

    Handles:
    - ** (bold)
    - * (italic)
    - ` (inline code)
    - ``` (code blocks)
    """
    # Count unclosed tags
    bold_count = text.count("**") % 2

    # Subtract bold asterisks from total to count italics
    total_asterisks = text.count("*")
    italic_count = (total_asterisks - bold_count * 2) % 2

    # Inline code
    inline_code_count = text.count("`") - text.count("```") * 3
    inline_code_unclosed = inline_code_count % 2

    # Code blocks
    code_block_count = text.count("```") % 2

    # Build closing tags (order matters!)
    closing = ""
    if code_block_count:
        closing += "```"
    if inline_code_unclosed:
        closing += "`"
    if bold_count:
        closing += "**"
    if italic_count:
        closing += "*"

    if closing:
        print(f"[MARKDOWN] Closing unclosed tags: {closing}")
        text = text + closing

    return text
```

**Testing**:
```python
# Test cases
assert ensure_valid_markdown("Hello **world") == "Hello **world**"
assert ensure_valid_markdown("Code: `print(") == "Code: `print(`"
assert ensure_valid_markdown("```python\ndef foo():") == "```python\ndef foo():```"
```

#### Step 2: Update Bot to Use Helpers
**File**: `/Users/terryli/.claude/automation/lychee/runtime/bot/multi-workspace-bot.py`

**Changes**:
1. Import helper module:
   ```python
   from runtime.lib.telegram_helpers import (
       safe_edit_message,
       safe_send_message,
       ensure_valid_markdown
   )
   ```

2. Replace direct calls with safe wrappers:
   ```python
   # BEFORE
   await query.edit_message_text(text, parse_mode="Markdown")

   # AFTER
   await safe_edit_message(query, text)
   ```

3. Update all 8 locations systematically

**Risk**: Low (wrapper pattern, no logic changes)

#### Step 3: Add Dependency
**File**: `/Users/terryli/.claude/automation/lychee/runtime/bot/multi-workspace-bot.py`

Add to PEP 723 header:
```python
# /// script
# dependencies = [
#     "python-telegram-bot>=21.0",
#     "jsonschema>=4.0.0",
# ]
# ///
```

Already present - no change needed.

---

## Priority 2: Streaming Progress Updates

### Problem Statement
**Current UX**: User sees "Processing..." for 10-30 seconds with no feedback

**Desired UX**:
```
📊 Running workflow: Fix Docstrings
⏳ Loading files... (2s)
⏳ Analyzing docstrings... (5s)
⏳ Applying fixes... (8s)
✅ Completed: 15 files updated (12s)
```

### Architecture

**Option A: Orchestrator Emits Progress** (RECOMMENDED)
```
Orchestrator → Progress JSON → Bot Polls → Update Message
```

**Option B: Orchestrator Streams to Bot** (Complex)
```
Orchestrator → WebSocket/Pipe → Bot → Update Message
```

**Choose Option A** - simpler, proven pattern

### Implementation Steps

#### Step 1: Define Progress Schema
**File**: `/Users/terryli/.claude/automation/lychee/state/progress/`

**Schema** (`progress_{session_id}_{workspace_hash}.json`):
```json
{
  "workspace_id": "81e622b5",
  "session_id": "...",
  "workflow_id": "fix-docstrings",
  "status": "running",
  "stage": "analyzing",
  "progress_percent": 60,
  "message": "Analyzing docstrings in 15 files...",
  "timestamp": "2025-10-27T03:00:00Z"
}
```

#### Step 2: Orchestrator Emits Progress
**File**: `/Users/terryli/.claude/automation/lychee/runtime/orchestrator/multi-workspace-orchestrator.py`

**Add function**:
```python
def emit_progress(
    workspace_path: Path,
    session_id: str,
    workflow_id: str,
    stage: str,
    progress: int,
    message: str
):
    """Emit progress update for bot to display"""
    progress_file = PROGRESS_DIR / f"progress_{session_id}_{workspace_hash}.json"

    progress_data = {
        "workspace_id": workspace_hash,
        "session_id": session_id,
        "workflow_id": workflow_id,
        "status": "running",
        "stage": stage,
        "progress_percent": progress,
        "message": message,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    PROGRESS_DIR.mkdir(parents=True, exist_ok=True)
    progress_file.write_text(json.dumps(progress_data, indent=2))
```

**Add calls** in `_execute_workflow()`:
```python
async def _execute_workflow(...):
    # Start
    emit_progress(workspace_path, session_id, workflow_id, "starting", 0, "Starting workflow...")

    # Render template
    emit_progress(..., "rendering", 20, "Rendering prompt template...")
    prompt = render_workflow_prompt(workflow, context)

    # Start CLI
    emit_progress(..., "executing", 40, "Starting Claude CLI...")
    process = await asyncio.create_subprocess_exec(...)

    # Wait
    emit_progress(..., "waiting", 60, "Waiting for completion...")
    stdout, stderr = await process.communicate()

    # Complete
    emit_progress(..., "completed", 100, "Workflow completed")
```

#### Step 3: Bot Polls Progress
**File**: `/Users/terryli/.claude/automation/lychee/runtime/bot/multi-workspace-bot.py`

**Add polling task**:
```python
async def poll_progress_updates(app: Application):
    """Poll for progress updates and edit messages"""
    while True:
        await asyncio.sleep(2)  # Poll every 2 seconds

        # Scan progress directory
        if not PROGRESS_DIR.exists():
            continue

        progress_files = list(PROGRESS_DIR.glob("progress_*.json"))

        for progress_file in progress_files:
            try:
                with progress_file.open() as f:
                    progress = json.load(f)

                # Find associated message_id (stored in progress tracking)
                # Update message with progress

                # If completed, delete progress file
                if progress["status"] == "completed":
                    progress_file.unlink()

            except Exception as e:
                print(f"⚠️  Failed to process progress: {e}")
```

**Start polling**:
```python
async def main():
    # ... existing setup ...

    # Start background tasks
    monitor_task = asyncio.create_task(idle_timeout_monitor())
    scanner_task = asyncio.create_task(periodic_file_scanner(app))
    progress_task = asyncio.create_task(poll_progress_updates(app))  # NEW
```

**Risk**: Medium (new background task, message_id tracking needed)

---

## Testing Plan

### Phase 1: Rate Limiting (2-3 hours)
1. Create `telegram_helpers.py` module
2. Add unit tests for `ensure_valid_markdown()`
3. Test helper functions in isolation
4. Update bot.py incrementally (one handler at a time)
5. Restart bot and test each workflow
6. Monitor logs for rate limit handling

**Success Criteria**:
- No regressions in existing workflows
- 429 errors handled gracefully (logged, not crashed)
- Markdown validation working

### Phase 2: Markdown Safety (1 hour)
1. Test with intentionally broken markdown
2. Verify all messages render correctly
3. Check special cases (code blocks, nested formatting)

**Success Criteria**:
- No "can't parse entities" errors
- All workflow menus render correctly

### Phase 3: Streaming Progress (4-6 hours)
1. Add progress schema and directory
2. Update orchestrator with emit_progress calls
3. Test progress emission (verify JSON files created)
4. Add bot polling (without message updates first)
5. Add message_id tracking
6. Wire up message updates
7. Test end-to-end

**Success Criteria**:
- Progress updates visible in Telegram
- No performance degradation
- Clean cleanup on completion

---

## Rollback Triggers

Immediately revert if:
- ❌ Bot crashes and doesn't restart
- ❌ Existing workflows fail (lychee-autofix, prune-legacy, etc.)
- ❌ Rate limit causes bot ban
- ❌ Messages fail to send/edit consistently
- ❌ Performance degradation >20%

Monitor:
- Error rate in logs
- Message delivery success rate
- Bot responsiveness
- Telegram API errors

---

## Estimated Timeline

| Phase | Effort | Completion |
|-------|--------|------------|
| **P1: Rate Limiting** | 2-3 hours | Day 1 |
| **P1: Markdown Safety** | 1 hour | Day 1 |
| **Testing P1** | 1 hour | Day 1 |
| **P2: Progress Schema** | 1 hour | Day 2 |
| **P2: Orchestrator Updates** | 2 hours | Day 2 |
| **P2: Bot Polling** | 2-3 hours | Day 2-3 |
| **Testing P2** | 1-2 hours | Day 3 |
| **Total** | **10-13 hours** | **3 days** |

---

## Implementation Order

1. **Day 1 Morning**: Create telegram_helpers.py + tests
2. **Day 1 Afternoon**: Update bot.py with safe wrappers
3. **Day 1 Evening**: Test and validate P1
4. **Day 2 Morning**: Add progress schema + orchestrator updates
5. **Day 2 Afternoon**: Add bot polling logic
6. **Day 2 Evening**: Wire up message updates
7. **Day 3**: End-to-end testing + bug fixes

---

## Next Steps

**Immediate**:
1. Create feature branch: `feature/telegram-improvements`
2. Backup current bot: `cp multi-workspace-bot.py multi-workspace-bot.py.backup`
3. Begin Phase 1: Create telegram_helpers.py

**Ready to proceed?**
