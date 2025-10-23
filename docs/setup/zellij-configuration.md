# Zellij Configuration: Balanced Power-User Setup

Comprehensive guide to Zellij's historical tracking, scrollback, and session serialization settings for optimal development workflows.

## Current Configuration: Balanced Power-User Profile

Your Zellij setup is optimized for feature engineering, ML development, and extensive logging workflows:

```kdl
# ~/.config/zellij/config.kdl
scroll_buffer_size 50000                    # 5x default: extensive log history
session_serialization true                  # Automatic state saving
serialize_pane_viewport true                # Save visible content on screen
scrollback_lines_to_serialize 10000         # Recover up to 10K lines after crashes
serialization_interval 60                   # Save session state every 60 seconds
scrollback_editor "hx"                      # Edit scrollback with Helix
auto_exit_zellij_on_quit true               # Prevent nested shells
```

**Result**:

- Per-pane memory: ~8 MB (vs 1.6 MB default)
- Per-session disk: 100-250 KB
- Crash recovery: Last 10,000 lines + viewport
- Performance: Negligible overhead

---

## Historical Tracking Explained

### Scroll Buffer vs. Serialization

**`scroll_buffer_size` (50000)**

- Lines stored in **memory** per pane
- Available immediately when scrolling up (`Ctrl+S`)
- Lost when pane closes or session exits
- Independent of crash recovery
- **Your use case**: Large training logs, debug output, build logs

**`scrollback_lines_to_serialize` (10000)**

- Lines saved to **disk** when session closes/crashes
- Restored automatically on `zellij attach`
- Survives system restarts and crashes
- Paired with `serialize_pane_viewport`
- **Your use case**: Context preservation after unexpected termination

**Key distinction:**

- Want to scroll back immediately? Use larger `scroll_buffer_size`
- Want to recover history after crash? Use larger `scrollback_lines_to_serialize`

---

## Configuration Options by Use Case

### Option 1: Balanced Power-User (Current - Recommended)

```kdl
scroll_buffer_size 50000
scrollback_lines_to_serialize 10000
serialize_pane_viewport true
serialization_interval 60
scrollback_editor "hx"
```

**Best for**: Feature engineering, ML workflows, debugging

- Extensive immediate history (50K lines in memory)
- Good crash recovery (10K lines to disk every 60s)
- ~8 MB per pane memory
- ~100-250 KB per session disk

---

### Option 2: Maximum Protection

```kdl
scroll_buffer_size 100000
scrollback_lines_to_serialize 0             # Unlimited
serialize_pane_viewport true
serialization_interval 10                   # Save every 10s
scrollback_editor "hx"
```

**Best for**: Mission-critical work, long-running processes, production debugging

- Extreme history: 100K lines in memory
- Near-complete recovery (no limits)
- Frequent saves minimize data loss (<10s)
- **Cost**: High disk writes, frequent I/O, potential disk wear
- ~16 MB per pane memory
- Disk usage can reach 1-5 MB per session

---

### Option 3: Conservative (Low-Resource)

```kdl
scroll_buffer_size 10000                    # Default
scrollback_lines_to_serialize 1000
serialize_pane_viewport false               # Skip viewport
serialization_interval 300                  # Save every 5 minutes
scrollback_editor "hx"
```

**Best for**: Low-memory systems, many concurrent panes, minimal overhead

- Moderate immediate history (10K lines)
- Minimal recovery capability
- Layout still recovers, but no scrollback history
- ~1.6 MB per pane memory
- <20 KB per session disk

---

### Option 4: Zero Recovery (No Serialization)

```kdl
scroll_buffer_size 10000
session_serialization false                 # Disable all saving
serialize_pane_viewport false
scrollback_lines_to_serialize 0
```

**Best for**: Temporary sessions, ephemeral work

- Pure in-memory multiplexer
- No disk overhead
- Nothing survives session close
- ~1.6 MB per pane memory

---

## Memory vs. Disk Tradeoffs

| Setting                | Memory/Pane | Disk/Session | Recovery     | Performance |
| ---------------------- | ----------- | ------------ | ------------ | ----------- |
| **Default (10K)**      | 1.6 MB      | 20-50 KB     | Layout only  | Fast        |
| **Balanced (50K/10K)** | 8 MB        | 100-250 KB   | Full context | Good        |
| **Maximum (100K/0)**   | 16 MB       | 500KB-5MB    | Complete     | Sluggish    |
| **Conservative**       | 1.6 MB      | <20 KB       | Minimal      | Fast        |

---

## Performance Impact Analysis

### Memory Growth

**Per-pane estimates** (80 characters average line width):

| Lines     | Memory | Comparison     |
| --------- | ------ | -------------- |
| 10,000    | 1.6 MB | Default Zellij |
| 50,000    | 8 MB   | Your current   |
| 100,000   | 16 MB  | Maximum        |
| 1,000,000 | 160 MB | Warning zone   |

**Scaling with multiple panes:**

- 5 panes × 50K lines = 40 MB session memory
- 10 panes × 50K lines = 80 MB session memory
- Monitor with `top` or `ps aux | grep zellij`

### Disk I/O

**Serialization writes per minute:**

- `serialization_interval 60` = 1 write/minute (minimal)
- `serialization_interval 10` = 6 writes/minute (noticeable on HDD)
- `serialization_interval 1` = 60 writes/minute (audible disk noise)

**Typical disk usage growth:**

```
Day 1:   ~100 KB per active session
Week 1:  ~1-2 MB (old snapshots auto-cleaned)
Month 1: ~2-5 MB (steady state, Zellij cleans old data)
```

---

## Critical Issue: Very Long Lines

⚠️ **Known Limitation**: Lines with 2000+ characters cause **exponential memory usage**

**Example**:

```
10,000 lines × 80 chars  = 1.6 MB  ✓
10,000 lines × 2000 chars = 1.2 GB ✗ (crashes!)
```

**Prevention**:

```bash
# Bad (huge output crashes scrollback):
echo "$(cat huge-file)" | sed 's/pattern/replacement/g'

# Good (output to file instead):
command > output.log
tail -f output.log
```

---

## Practical Workflows

### Debugging with Scrollback

**Access scrollback editor:**

```
Ctrl+S              # Enter scroll mode
e                   # Open in Helix
```

**Search in Helix:**

```
/pattern            # Search
n                   # Next match
N                   # Previous match
```

**Export scrollback to file:**

```
Ctrl+S
e
:w /tmp/debug.log   # Save from Helix
:q                  # Exit
```

---

### Monitoring Disk Usage

```bash
# Check total cache
du -sh ~/.cache/zellij/

# Clean all sessions (⚠️ destroys saved sessions)
zellij delete-all-sessions

# List session files
find ~/.cache/zellij -type f -name "*.kdl" | wc -l

# Monitor writes in real-time
# (Requires superuser)
sudo iotop | grep -i zellij
```

---

## Comparison with Other Multiplexers

### Zellij vs. tmux

| Feature                | Zellij                | tmux                    |
| ---------------------- | --------------------- | ----------------------- |
| Default scrollback     | 10,000                | 2,000                   |
| Memory efficiency      | Lower (Rust overhead) | Higher                  |
| Session persistence    | Built-in              | Plugin (tmux-resurrect) |
| Automatic recovery     | Yes (if configured)   | Manual                  |
| Viewport serialization | Configurable          | N/A                     |
| Empty session memory   | 80 MB                 | 6 MB                    |

**For your use case (feature engineering):**

- Zellij superior due to built-in crash recovery
- Memory overhead acceptable for development work
- Serialization more reliable than tmux plugins

### Zellij vs. screen

| Feature             | Zellij   | screen         |
| ------------------- | -------- | -------------- |
| Default scrollback  | 10,000   | 100-1,024      |
| Recommended         | 50,000   | 10,000-200,000 |
| Session persistence | Modern   | Legacy         |
| Memory usage        | Moderate | Light          |

---

## Cross-Machine Sync Considerations

### Session Serialization Format

Sessions are saved as human-readable KDL files:

```bash
~/.cache/zellij/
├── session-name-uuid1/
│   ├── layout.kdl           # Pane structure
│   ├── session.kdl          # Running state
│   └── sessions.kdl         # Metadata
└── session-name-uuid2/
    └── ...
```

### Sharing Sessions Between Machines

```bash
# Export session from machine A
zellij action dump-layout > ~/my-session.kdl

# Copy to machine B
scp ~/my-session.kdl user@machineB:~

# Start with exported layout on machine B
zellij --layout ~/my-session.kdl --session restored
```

---

## Troubleshooting

### High Memory Usage

**Symptoms**: Zellij using >500 MB RAM

**Solutions**:

```kdl
# Reduce scrollback size
scroll_buffer_size 25000        # Instead of 50000

# Reduce serialization lines
scrollback_lines_to_serialize 5000  # Instead of 10000

# Check for very long lines
# (problematic output will crash scrollback)
```

### Disk Usage Growing

**Symptoms**: `~/.cache/zellij/ > 500 MB`

**Solutions**:

```bash
# Reduce serialization
scrollback_lines_to_serialize 1000

# Increase serialization interval (less frequent saves)
serialization_interval 300      # Save every 5 minutes

# Clean old sessions
zellij delete-all-sessions
```

### Sluggish Terminal Resizing

**Symptoms**: Terminal lags when resizing with large buffers

**Solution**:

```kdl
# Reduce scrollback (fewer lines to recalculate on resize)
scroll_buffer_size 25000

# Or use external paging instead of scrollback
# pipe large output to less instead
```

---

## Monitoring Configuration Health

### Monthly Checklist

```bash
# 1. Check cache size
du -sh ~/.cache/zellij/

# 2. List active sessions
zellij ls

# 3. Monitor memory
top -p $(pgrep zellij)

# 4. Verify config parsing
zellij setup --check

# 5. Review recent sessions
zellij ls --exited | head -5
```

---

## References

### Official Documentation

- [Zellij Configuration Options](https://zellij.dev/documentation/options.html)
- [Session Resurrection](https://zellij.dev/documentation/session-resurrection.html)
- [Scrollback Management](https://zellij.dev/documentation/)

### Your Workspace

- [Zellij Cheatsheet](zellij-cheatsheet.md) - Printable command reference
- [Session Recovery](zellij-session-recovery.md) - Auto-recovery procedures
- [Terminal Setup](terminal-setup.md) - Ghostty + Zellij integration

---

## See Also

- [Credential Management: Doppler](credential-management.md)
- [Terminal Setup: Ghostty + Helix](terminal-setup.md)
- [SSH Clipboard: OSC52](ssh-clipboard-osc52.md)
