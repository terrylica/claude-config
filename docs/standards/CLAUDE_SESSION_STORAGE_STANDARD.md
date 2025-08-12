# Claude Code Session Storage: Verified Standard (2025-08-12)

This document records definitive, empirical evidence for how official Claude Code stores sessions, and how our workspace deviated from it. It replaces assumptions with proof.

## Summary (Authoritative)

- Official location: `$HOME/.claude/projects/`
- Per-workspace folders: encoded absolute path of CWD (slashes → hyphens)
- File format: JSONL, one event per line, UUID filenames
- Confirmed by fully isolated Docker test (Ubuntu 24.04 + npm global install)

## Empirical Evidence

We ran a clean, isolated test:

1. Built Docker image (Ubuntu 24.04), installed Node.js and `@anthropic-ai/claude-code` globally.
2. Created user `testuser`, ran `claude` in `/home/testuser/my-project`.
3. Results inside container (key excerpts):

```
$HOME/.claude/
  projects/
    -home-testuser-my-project/
      364695f1-13e7-4cbb-ad4b-0eb416feb95d.jsonl
  statsig/
  shell-snapshots/
  todos/
```

Therefore, official Claude Code stores sessions under `~/.claude/projects/` using encoded path directories.

## Our Previous Deviation (Explained)

- We had symlinks in `~/.claude`:
  - `projects -> system/sessions`
  - `ide -> system/ide`, `statsig -> system/statsig`, `todos -> system/todos`
- Active sessions lived in `~/.claude/system/sessions/…` (non-standard), and tooling referenced that path.
- This customization caused path confusion and tooling failures (e.g., SAGE), masking the official behavior.

## Why We Are Certain

- Reproduced behavior in a hermetic Docker container.
- No host config, no local aliases, no symlinks: pure upstream behavior.
- Observed creation of `projects/` and an encoded per-project folder with a `.jsonl` session file.

## Migration Guidance

- Preferred: Align to the official standard and write tools against `~/.claude/projects/`.
- If custom layout is retained, ensure tools resolve `~/.claude/projects/` faithfully (avoid symlink surprises).
- For cross-host sync, mirror `~/.claude/projects/` and preserve timestamps.

## Verification Commands

```bash
ls -la ~/.claude/projects/
find ~/.claude/projects/ -name "*.jsonl" -type f | head -5
head -n 1 ~/.claude/projects/*/*.jsonl | python -m json.tool
```

## Decision

Adopt `~/.claude/projects/` as the authoritative session root. Update internal docs, tools, and scripts to treat it as the single source of truth.


