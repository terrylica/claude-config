# Claude Code GPU Workstation Synchronization Strategy

## Overview

This document outlines the optimal synchronization strategy between macOS Claude Code and remote GPU workstation Claude Code for the SAGE meta-framework implementation.

## Current Setup Analysis

### Local Environment (macOS)
- **Location**: `/Users/terryli/eon/nt/`
- **Repository**: `https://github.com/Eon-Labs/nt.git`
- **Branch**: `master`
- **Claude Code**: Full access to local development environment
- **Limitations**: No GPU for TiRex model inference

### Remote Environment (GPU Workstation)
- **Connection**: ZeroTier network `db64858fedbf2ce1`
- **Host**: `zerotier-remote` (172.25.253.142)
- **User**: `tca`
- **Expected GPU**: CUDA-capable for TiRex inference
- **Status**: Currently offline (connection test failed)

## Strategy 1: Git Worktree + SSH Development (RECOMMENDED)

### Architecture
```
Local macOS (Development & Planning)     Remote GPU (Model Inference & Validation)
├── /Users/terryli/eon/nt/              ├── ~/eon/nt-worktree-main/
│   ├── .git/ (main repository)         │   ├── (linked to local .git)
│   ├── docs/ (strategy & planning)     │   ├── models/ (GPU-specific code)
│   ├── nautilus_test/                  │   ├── notebooks/ (TiRex validation)
│   └── repos/ (all SAGE models)        │   └── gpu_validation/
├── GitHub: Eon-Labs/nt                 └── ~/eon/nt-worktree-gpu/
│   └── Centralized source of truth         └── (GPU-specific branches)
```

### Implementation Steps

#### Phase 1: Repository Structure Setup
1. **Local Git Worktree Configuration**:
   ```bash
   cd ~/eon/nt
   git worktree add ~/eon/nt-gpu gpu-validation  # Create GPU-specific branch
   git push -u origin gpu-validation
   ```

2. **Remote Environment Setup** (when GPU workstation is online):
   ```bash
   # On GPU workstation via SSH
   gpu  # Use our new alias
   git clone https://github.com/Eon-Labs/nt.git ~/eon/nt
   cd ~/eon/nt
   git worktree add ~/eon/nt-gpu gpu-validation
   ```

#### Phase 2: Development Workflow

**Local Development (macOS)**:
- Strategy development and documentation
- AlphaForge integration (CPU compatible)
- catch22 + tsfresh feature extraction
- Code development and testing
- Git commits to `master` branch

**Remote Validation (GPU Workstation)**:
- TiRex model inference and validation
- GPU-accelerated computations
- Model performance benchmarking
- Results logging and analysis
- Git commits to `gpu-validation` branch

#### Phase 3: Synchronization Protocol

**Daily Sync Process**:
```bash
# 1. Local: Push changes to GitHub
git add . && git commit -m "Local development updates"
git push origin master

# 2. Remote: Pull updates and run GPU validation
gpu
cd ~/eon/nt && git pull origin master
cd ~/eon/nt-gpu && git merge master
# Run TiRex validation...
git add . && git commit -m "GPU validation results"
git push origin gpu-validation

# 3. Local: Merge GPU results
git pull origin gpu-validation
git merge gpu-validation
```

### Advantages
✅ **True distributed development** with specialized environments  
✅ **Git history preservation** with proper branching strategy  
✅ **Automatic conflict resolution** via GitHub merge/PR workflow  
✅ **Independent Claude Code instances** optimized for each environment  
✅ **Bandwidth efficient** (only sync code changes, not data)  

### Limitations
⚠️ **Requires GPU workstation to be online** for TiRex validation  
⚠️ **Manual sync discipline** required for consistency  
⚠️ **Claude Code SSH authentication issues** (known bug #1178)  

## Strategy 2: Hybrid Rsync + Git Backup

### Architecture
- **Primary Development**: Local macOS with full Claude Code integration
- **GPU Computation**: Rsync code to GPU workstation, run inference, rsync results back
- **Version Control**: Git commits from macOS only

### Implementation
```bash
# Sync to GPU workstation
gpu-sync-to  # Use our new alias

# SSH to GPU workstation and run TiRex validation
gpu
cd ~/eon/nt && python -m sage.tirex_validation

# Sync results back to macOS
exit
gpu-sync-from
```

### Advantages
✅ **Simple workflow** with single source of truth  
✅ **Full Claude Code integration** on macOS  
✅ **Fast synchronization** with rsync  
✅ **No Git complexity** on remote machine  

### Limitations
⚠️ **Manual sync required** for each GPU operation  
⚠️ **Risk of data loss** if sync fails  
⚠️ **No version control** on GPU workstation  

## Strategy 3: Remote Claude Code Installation

### Architecture
- **Dual Claude Code Setup**: Independent instances on both machines
- **Shared Repository**: GitHub as synchronization hub
- **Specialized Workflows**: Each environment optimized for its strengths

### Implementation Steps
1. **Install Claude Code on GPU Workstation**:
   ```bash
   gpu
   curl -sSL https://claude.ai/code/install | sh
   ```

2. **Configure Shared GitHub Repository**:
   - Both instances commit to different branches
   - Regular merge/rebase operations for synchronization

### Advantages
✅ **Full Claude Code functionality** on both machines  
✅ **Independent development** with AI assistance everywhere  
✅ **Professional workflow** with proper version control  

### Limitations
⚠️ **Complex setup** and maintenance  
⚠️ **SSH authentication issues** with Claude Code  
⚠️ **Potential conflicts** between AI development decisions  

## Recommended Implementation Plan

### Phase 1: Immediate Setup (Today)
1. ✅ **GPU Connection Aliases** - Already implemented
2. **Test GPU Workstation Connection** - Wait for workstation to come online
3. **Strategy 2 Implementation** - Quick rsync-based workflow for immediate TiRex testing

### Phase 2: Medium-term (Next Week)
1. **Strategy 1 Implementation** - Git worktree setup when GPU workstation stable
2. **Claude Code Remote Setup** - If SSH authentication issues resolved
3. **Automated Sync Scripts** - Cron jobs or Git hooks for synchronization

### Phase 3: Long-term (Production)
1. **CI/CD Pipeline** - GitHub Actions for automatic validation
2. **Monitoring Setup** - GPU workstation health and availability
3. **Backup Strategy** - Regular snapshots of both environments

## Quick Commands Summary

```bash
# Connection Management
gpu              # Quick SSH to GPU workstation
gpu-check        # Test connection availability
zt-status        # Check ZeroTier network status

# Development Workflow  
gpu-sync-to      # Sync local changes to remote
gpu-sync-from    # Sync remote results to local backup
gpu-status       # Check GPU memory and availability

# TiRex-Specific Operations
gpu-tirex-test   # Quick PyTorch/CUDA availability test
gpu-tmux         # Connect with persistent tmux session
```

## Troubleshooting

### GPU Workstation Offline
- **Check ZeroTier Status**: `zt-status`
- **Restart ZeroTier**: `zt-restart` (if needed)
- **Contact Network Admin**: If workstation hardware issues

### Sync Conflicts
- **Use Git Worktree Strategy**: Proper branching prevents conflicts
- **Manual Resolution**: Standard Git merge conflict resolution
- **Backup Strategy**: Always maintain local backups before major syncs

### Performance Issues
- **Rsync Optimization**: Use `--exclude` patterns for large files
- **Git LFS**: For large model files or datasets
- **Compression**: Enable SSH compression for slow connections

---

**Status**: Implementation ready - waiting for GPU workstation to come online  
**Next Action**: Test connection and implement Strategy 2 for immediate TiRex validation  
**Created**: 2025-07-31