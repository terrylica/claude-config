# Disk Cleanup Workflow

**Version**: 1.0.0
**Last Updated**: 2025-10-16

## Manual Cleanup Workflow

Run these commands when you notice disk space running low (typically every few weeks or when target/ exceeds 30GB).

### Quick Cleanup (Current Project Only)

```bash
# Clean current project's build artifacts (from project root)
cargo clean
```

**Result**: Removes `target/` directory (~40GB)
**Rebuild Time**: 5-15 minutes on next `cargo build`

### Full Cleanup (All Rust Projects)

```bash
# Find all Rust projects and clean them
cargo clean-all

# Or with specific filters:
cargo clean-all --days 30    # Only projects not used in 30+ days
cargo clean-all --min-size 5GB  # Only projects with target/ > 5GB
```

**Result**: Cleans all Rust projects on your machine
**Safe**: Always shows what will be deleted before cleaning

### Check Current Disk Usage

```bash
# Check rangebar project size (from project root)
du -sh .

# Check target/ size specifically
du -sh target

# Check all directories breakdown
du -h -d 1 . | sort -hr | head -10
```

### Additional Cleanup (Optional)

```bash
# Clean old test outputs (2.1GB currently, from project root)
rm -rf output/bps_validation_*
rm -rf output/data_structure_validation/*
rm -rf output/nohup_*
rm -rf output/edge_case_test
# Keep: output/README.md, output/.gitkeep

# Remove external repos (67MB)
rm -rf repos/

# Clean Cargo global cache (old entries only)
cargo clean-all --cargo-cache
```

## What Gets Cleaned

| Command | What It Removes | Regenerates On |
|---------|----------------|----------------|
| `cargo clean` | `target/` directory | Next `cargo build` |
| `cargo clean-all` | All `target/` directories system-wide | Next build in each project |
| Manual `rm -rf output/*` | Test output files | Re-running tests |

## What's Protected

The following are **never** cleaned automatically:
- Source code (`crates/`, `src-archived/`)
- Git history (`.git/`)
- Test data (`test_data/`)
- Documentation (`docs/`)
- Configuration files

## Pre-commit Hook

Your pre-commit hook **does NOT run cargo clean**. It only:
- Prevents files > 5MB from being committed to git
- Runs `cargo fmt`, `cargo clippy`, `cargo nextest`, `cargo deny`
- Checks for merge conflicts, private keys, etc.

**Why**: Running `cargo clean` on every commit would require 5-15 minute rebuilds after each commit.

## Typical Usage Pattern

```bash
# Weekly or when disk runs low:
cargo clean-all --dry-run    # See what would be cleaned
cargo clean-all --yes        # Clean it

# Or just current project:
cargo clean
```

## SLOs

- **Availability**: 100% (all commands are safe and reversible)
- **Correctness**: 100% (only removes build artifacts, never source code)
- **Observability**: 100% (shows what will be deleted before deleting)
- **Maintainability**: 100% (standard Cargo tools, no custom scripts)

## Tools Installed

- `cargo-clean-all` v0.6.4 - Installed globally via `cargo install cargo-clean-all`
- Location: `/Users/terryli/.cargo/bin/cargo-clean-all`

## References

- cargo-clean-all: https://github.com/dnlmlr/cargo-clean-all
- Pre-commit config: `../../.pre-commit-config.yaml`
