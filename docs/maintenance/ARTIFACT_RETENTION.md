# Runtime Artifact Retention Policy

**Version**: 1.0.0
**Status**: Proposed
**Created**: 2025-10-23
**Purpose**: Define lifecycle management for runtime artifacts to prevent unbounded growth

---

## Overview

The `~/.claude/` workspace accumulates runtime artifacts from Claude Code sessions, debugging, and file history tracking. Without active management, these artifacts grow unbounded. This document establishes **retention policies** and **archival strategies** to maintain workspace health.

### Current State (as of 2025-10-23)

| Artifact Type | Location | Size | File Count | Growth Rate |
| --- | --- | --- | --- | --- |
| Shell Snapshots | `/shell-snapshots/` | 69 MB | 371 files | ~2-3 MB/week |
| Debug Logs | `/debug/` | 57 MB | Unknown | ~1-2 MB/week |
| File History | `/file-history/` | 63 MB | ~300 UUIDs | ~1-2 MB/week |
| Task Tracking | `/todos/` | 3.6 MB | 60+ files | ~100 KB/week |
| Session History | `/history.jsonl` | 1.2 MB | 1 file | ~50 KB/week |
| **Total** |  | **~210 MB** | **700+ files** | **~5-8 MB/week** |

**Projected Growth**: Without management, artifacts will reach **~500 MB within 6 months**.

---

## Retention Policies

### Policy 1: Time-Based Retention (30 Days)

**Applies to**: `shell-snapshots/`, `debug/`, `file-history/`

**Rule**: Keep artifacts modified within the last **30 days**, archive older artifacts.

**Rationale**:

- Active development typically references recent sessions
- 30 days provides sufficient buffer for investigation
- Older artifacts rarely accessed after 30 days

**Implementation**:

```bash
# Identify files older than 30 days
find /Users/terryli/.claude/shell-snapshots/ \
  -type f -mtime +30
```

---

### Policy 2: Compression on Archive

**Applies to**: All archived artifacts

**Rule**: Compress archived artifacts to `tar.gz` format before archival.

**Rationale**:

- Text-based logs compress well (typically 80-90% reduction)
- Maintains accessibility while reducing storage
- Standard format, easily extractable

**Implementation**:

```bash
# Archive and compress shell snapshots older than 30 days
tar -czf archive/shell-snapshots-2025-10.tar.gz \
  $(find shell-snapshots/ -type f -mtime +30)
```

**Expected Compression Ratios**:

- Text logs (shell snapshots, debug): **80-90% reduction**
- JSON data (file history, todos): **60-70% reduction**
- Mixed content: **70-80% reduction**

---

### Policy 3: Verification Before Deletion

**Applies to**: All cleanup operations

**Rule**: Never delete original files until archive verification succeeds.

**Verification Steps**:

1. Create compressed archive
2. Verify archive integrity: `tar -tzf archive.tar.gz > /dev/null`
3. Compare file counts: `tar -tzf archive.tar.gz | wc -l`
4. Test extraction: `tar -xzf archive.tar.gz -C /tmp/test/`
5. Only then delete originals

**Implementation**:

```bash
# Verify archive before deletion
if tar -tzf archive.tar.gz > /dev/null 2>&1; then
    echo "Archive valid, safe to delete originals"
else
    echo "Archive corrupt, DO NOT delete originals"
    exit 1
fi
```

---

## Artifact Categories & Policies

### 1. Shell Snapshots (`/shell-snapshots/`)

**Purpose**: Claude Code session shell output snapshots
**Current Size**: 69 MB (371 files)
**Ownership**: Claude Code (automatically generated)

#### Retention Policy

| Age | Action | Location |
| --- | --- | --- |
| 0-30 days | **Keep** | `/shell-snapshots/` |
| 30-90 days | **Archive** | `/archive/shell-snapshots-YYYY-MM.tar.gz` |
| 90+ days | **Delete archive** (optional) | N/A |

#### Archival Process

```bash
#!/usr/bin/env bash
# Monthly shell snapshot archival

MONTH=$(date -v-1m +%Y-%m)  # Previous month
ARCHIVE_DIR="/Users/terryli/.claude/archive"
SNAPSHOT_DIR="/Users/terryli/.claude/shell-snapshots"

# Find files older than 30 days
OLD_FILES=$(find "$SNAPSHOT_DIR" -type f -mtime +30)

if [ -z "$OLD_FILES" ]; then
    echo "No old snapshots to archive"
    exit 0
fi

# Create archive
tar -czf "$ARCHIVE_DIR/shell-snapshots-$MONTH.tar.gz" \
    $(find "$SNAPSHOT_DIR" -type f -mtime +30)

# Verify archive
if tar -tzf "$ARCHIVE_DIR/shell-snapshots-$MONTH.tar.gz" > /dev/null 2>&1; then
    echo "Archive created and verified"
    # Delete originals
    find "$SNAPSHOT_DIR" -type f -mtime +30 -delete
    echo "Old snapshots archived and deleted"
else
    echo "ERROR: Archive verification failed"
    exit 1
fi
```

#### Automation

**Method**: LaunchAgent (macOS) or cron job
**Schedule**: First day of each month
**Script**: `/tools/maintenance/archive-shell-snapshots.sh`

---

### 2. Debug Logs (`/debug/` → `/system/debug/`)

**Purpose**: Debugging output and error logs
**Current Size**: 57 MB
**Ownership**: Workspace scripts and tools

#### Retention Policy

| Age | Action | Location |
| --- | --- | --- |
| 0-30 days | **Keep** | `/system/debug/` |
| 30-180 days | **Archive** | `/archive/debug-logs-YYYY-MM.tar.gz` |
| 180+ days | **Delete archive** | N/A |

#### Special Considerations

- **Active debugging**: If actively debugging, keep all logs regardless of age
- **Error logs**: Preserve logs containing ERROR or FATAL for 180 days
- **Info logs**: Archive after 30 days

#### Selective Archival

```bash
# Archive info logs older than 30 days
find /system/debug/ -name "*info*.log" -mtime +30 | \
    tar -czf archive/debug-info-logs-$(date +%Y-%m).tar.gz -T -

# Archive error logs older than 180 days
find /system/debug/ -name "*error*.log" -mtime +180 | \
    tar -czf archive/debug-error-logs-$(date +%Y-%m).tar.gz -T -
```

---

### 3. File History (`/file-history/` → `/system/file-history/`)

**Purpose**: Claude Code file version tracking
**Current Size**: 63 MB (~300 UUID directories)
**Ownership**: Claude Code (automatically generated)

#### Retention Policy

| Age | Action | Location |
| --- | --- | --- |
| 0-30 days | **Keep** | `/system/file-history/` |
| 30-90 days | **Archive** | `/archive/file-history-YYYY-MM.tar.gz` |
| 90+ days | **Delete archive** | N/A |

#### Critical Warning

⚠️ **HIGH RISK**: File history may be actively referenced by Claude Code. Test thoroughly after archival.

**Pre-Archival Checklist**:

- [ ] Verify Claude Code can still access recent file history
- [ ] Test file history feature in Claude Code
- [ ] Create backup before archival
- [ ] Archive only directories older than 30 days

#### Archival Process

```bash
# Archive file history UUIDs older than 30 days
find /system/file-history/ -type d -mindepth 1 -maxdepth 1 -mtime +30 | \
    tar -czf archive/file-history-$(date +%Y-%m).tar.gz -T -

# Verify Claude Code file history still works
echo "Test file history in Claude Code before deleting originals"
```

---

### 4. Task Tracking (`/todos/` → `/system/todos/`)

**Purpose**: Claude Code task tracking JSON files
**Current Size**: 3.6 MB (60+ files)
**Ownership**: Claude Code (automatically generated)

#### Retention Policy

| Age | Action | Location |
| --- | --- | --- |
| 0-7 days | **Keep** | `/system/todos/` |
| 7-30 days | **Archive** | `/archive/todos-YYYY-MM.tar.gz` |
| 30+ days | **Delete archive** | N/A |

#### Notes

- Task files typically associated with sessions
- Once session complete, task files rarely needed
- Shorter retention (7 days) appropriate

---

### 5. Session History (`/history.jsonl` → `/system/history/session-history.jsonl`)

**Purpose**: Session history log
**Current Size**: 1.2 MB (single file)
**Ownership**: Claude Code

#### Retention Policy

**Special case**: Single growing file, not directory

| Size | Action |
| --- | --- |
| < 5 MB | **Keep as-is** |
| 5-10 MB | **Rotate and archive** |
| 10+ MB | **Split into monthly archives** |

#### Rotation Process

```bash
# When file exceeds 5 MB, rotate
if [ $(stat -f%z history.jsonl) -gt 5242880 ]; then
    mv history.jsonl history-$(date +%Y-%m).jsonl
    gzip history-$(date +%Y-%m).jsonl
    touch history.jsonl
fi
```

---

## Archival Directory Structure

### Target Organization

```
/Users/terryli/.claude/archive/
├── shell-snapshots-2025-10.tar.gz    # October 2025 snapshots
├── shell-snapshots-2025-09.tar.gz    # September 2025 snapshots
├── debug-logs-2025-10.tar.gz         # October 2025 debug logs
├── debug-logs-2025-09.tar.gz         # September 2025 debug logs
├── file-history-2025-10.tar.gz       # October 2025 file history
├── file-history-2025-09.tar.gz       # September 2025 file history
├── todos-2025-10.tar.gz              # October 2025 task files
├── history-2025-10.jsonl.gz          # October 2025 session history
└── README.md                         # Explains archive contents
```

### Archive README Template

````markdown
# Archived Runtime Artifacts

This directory contains compressed archives of old runtime artifacts.

## Contents

- **shell-snapshots-YYYY-MM.tar.gz**: Shell session snapshots from YYYY-MM
- **debug-logs-YYYY-MM.tar.gz**: Debug logs from YYYY-MM
- **file-history-YYYY-MM.tar.gz**: File version history from YYYY-MM
- **todos-YYYY-MM.tar.gz**: Task tracking data from YYYY-MM
- **history-YYYY-MM.jsonl.gz**: Session history from YYYY-MM

## Retention

Archives are kept for 90-180 days depending on type. See
/docs/maintenance/ARTIFACT_RETENTION.md for full policy.

## Extraction

To extract an archive:

```bash
tar -xzf shell-snapshots-2025-10.tar.gz -C /tmp/restored/
```
````

## Size Reduction

These archives achieve ~70-85% compression compared to originals.

````

---

## Automation Strategy

### Recommended Automation

#### Option 1: LaunchAgent (macOS)

Create `~/Library/LaunchAgents/com.claude.artifact-archival.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.claude.artifact-archival</string>

    <key>ProgramArguments</key>
    <array>
        <string>/Users/terryli/.claude/tools/maintenance/archive-artifacts.sh</string>
    </array>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Day</key>
        <integer>1</integer>
        <key>Hour</key>
        <integer>2</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>/Users/terryli/.claude/logs/artifact-archival.log</string>

    <key>StandardErrorPath</key>
    <string>/Users/terryli/.claude/logs/artifact-archival.error.log</string>
</dict>
</plist>
````

**Schedule**: First day of each month at 2:00 AM

#### Option 2: Cron Job (Linux/macOS)

```bash
# Edit crontab
crontab -e

# Add line:
0 2 1 * * /Users/terryli/.claude/tools/maintenance/archive-artifacts.sh
```

**Schedule**: First day of each month at 2:00 AM

---

## Manual Archival Procedure

For immediate cleanup or one-time archival:

### Step 1: Backup Workspace

```bash
/Users/terryli/.claude/tools/emergency-backup.sh
```

### Step 2: Run Archival Script

```bash
/Users/terryli/.claude/tools/maintenance/archive-artifacts.sh
```

### Step 3: Verify Archives

```bash
# List archive contents
tar -tzf archive/shell-snapshots-2025-10.tar.gz | head -20

# Verify integrity
tar -tzf archive/shell-snapshots-2025-10.tar.gz > /dev/null && \
    echo "Archive valid"
```

### Step 4: Test Systems

- Test Claude Code file history
- Verify task tracking works
- Check debug logging active

### Step 5: Monitor Space

```bash
# Check space recovery
du -sh shell-snapshots/ debug/ file-history/ todos/
```

---

## Monitoring & Alerts

### Space Monitoring

Create `/tools/monitoring/check-artifact-size.sh`:

```bash
#!/usr/bin/env bash
# Alert if artifacts exceed thresholds

SHELL_SNAPSHOTS=$(du -sm shell-snapshots 2>/dev/null | awk '{print $1}')
DEBUG_LOGS=$(du -sm debug 2>/dev/null | awk '{print $1}')
FILE_HISTORY=$(du -sm file-history 2>/dev/null | awk '{print $1}')

# Alert thresholds (MB)
THRESHOLD=100

if [ "$SHELL_SNAPSHOTS" -gt "$THRESHOLD" ]; then
    echo "WARNING: shell-snapshots is ${SHELL_SNAPSHOTS}MB (threshold: ${THRESHOLD}MB)"
fi

if [ "$DEBUG_LOGS" -gt "$THRESHOLD" ]; then
    echo "WARNING: debug is ${DEBUG_LOGS}MB (threshold: ${THRESHOLD}MB)"
fi

if [ "$FILE_HISTORY" -gt "$THRESHOLD" ]; then
    echo "WARNING: file-history is ${FILE_HISTORY}MB (threshold: ${THRESHOLD}MB)"
fi
```

---

## Rollback & Recovery

### Restore from Archive

```bash
# Extract archived snapshots
tar -xzf archive/shell-snapshots-2025-10.tar.gz -C shell-snapshots/

# Extract specific file
tar -xzf archive/debug-logs-2025-10.tar.gz \
    -C /tmp/ \
    "debug/2025-10-15-error.log"
```

### Emergency Recovery

If archival caused issues:

1. **Stop archival**: Kill any running archival processes
2. **Restore from backup**: Use emergency backup
3. **Extract archives**: Restore from compressed archives
4. **Verify systems**: Test Claude Code functionality
5. **Document issue**: Record in `/docs/maintenance/REORGANIZATION_ISSUES.md`

---

## Best Practices

### DO

✅ Always verify archives before deleting originals
✅ Keep recent artifacts (< 30 days)
✅ Use compression for all archives
✅ Test systems after archival
✅ Monitor artifact growth regularly
✅ Automate archival process
✅ Document exceptions to retention policy

### DON'T

❌ Delete artifacts without archiving
❌ Archive without verification
❌ Ignore Claude Code dependencies
❌ Let artifacts grow unbounded
❌ Archive active debugging sessions
❌ Delete archives prematurely

---

## Related Documentation

- [Workspace Reorganization Specification](/specifications/workspace-reorganization.yaml) - Overall plan
- [Cleanup Targets Specification](/specifications/reorg-cleanup-targets.yaml) - Specific cleanup targets
- [Reorganization Move Map](/specifications/reorg-move-map.yaml) - File moves
- [Workspace Health Check](/specifications/workspace-health-check.yaml) - Validation

---

## Implementation Timeline

| Phase | Action | Timeline |
| --- | --- | --- |
| **Phase 1** | Create archival scripts | Week 1 |
| **Phase 2** | Test manual archival | Week 1 |
| **Phase 3** | Set up automation | Week 2 |
| **Phase 4** | Monitor and adjust | Ongoing |

---

**Status**: Proposed policy for workspace reorganization
**Next Steps**: Create archival scripts, test thoroughly, implement automation
**Questions**: Document in `/docs/maintenance/WORKSPACE_REORGANIZATION_GUIDE.md`
