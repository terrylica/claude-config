# Bidirectional Sync Demo & Setup

## ✅ Current Status: Claude Code Installed on GPU Workstation

### Installation Complete:
- **Node.js**: v22.17.0 ✅
- **Claude Code**: v1.0.64 ✅ 
- **PATH**: Configured for user access ✅
- **Workspace**: ~/eon/nt/ ready ✅

## 🔄 Bidirectional Sync Flow

### Scenario 1: Develop on GPU Workstation → Sync to macOS
```bash
# SSH to GPU workstation
ssh zerotier-remote

# Navigate to synced workspace
cd ~/eon/nt/

# Start Claude Code development
export PATH=~/.npm-global/bin:$PATH
claude

# Edit files with Claude Code on GPU workstation
# → All changes automatically sync back to macOS in ~10 seconds
```

### Scenario 2: Develop on macOS → Sync to GPU Workstation  
```bash
# Work locally on macOS
cd ~/eon/nt/
# Edit with local Claude Code
# → Changes sync to GPU workstation in ~10 seconds

# Switch to GPU workstation
ssh zerotier-remote
cd ~/eon/nt/
# Files already updated and ready
```

## 🎯 Optimal Workflow for SAGE Development

### Primary Development: GPU Workstation (Recommended)
**Why GPU workstation as primary?**
- ✅ **TiRex model access** - Direct GPU for inference
- ✅ **No network latency** - All computation local
- ✅ **Full Claude Code features** - AI assistance where compute happens
- ✅ **Real-time GPU monitoring** - nvidia-smi, htop, etc.

### Backup/Reference: macOS
- ✅ **Automatic backup** of all work via Syncthing
- ✅ **Documentation viewing** - Rich documentation on local machine
- ✅ **Offline access** - Continue work without network
- ✅ **Local tools** - Your familiar macOS environment

## 🚀 Complete Setup Commands

### 1. Start Syncthing (if not running)
```bash
# On macOS (should already be running)
brew services status syncthing

# On GPU workstation  
ssh zerotier-remote "~/bin/syncthing --no-browser --no-restart > ~/syncthing.log 2>&1 &"
```

### 2. Configure Shared Folder (via Web Interface)
1. Open http://localhost:8384
2. Add folder: `/Users/terryli/eon/nt/` → Share with GPU workstation
3. Accept on remote side

### 3. Start Development Session
```bash
# Connect to GPU workstation
ssh zerotier-remote

# Navigate to synced workspace  
cd ~/eon/nt/

# Start Claude Code
export PATH=~/.npm-global/bin:$PATH
claude

# Begin SAGE development with full AI assistance + GPU access
```

## 📊 Sync Performance Testing

### Test the bidirectional sync:

#### From macOS → GPU Workstation:
```bash
# On macOS
echo "Test from macOS $(date)" > ~/eon/nt/sync-test-mac.txt

# Check on GPU workstation (~10 seconds later)
ssh zerotier-remote "cat ~/eon/nt/sync-test-mac.txt"
```

#### From GPU Workstation → macOS:
```bash
# On GPU workstation
ssh zerotier-remote 'echo "Test from GPU $(date)" > ~/eon/nt/sync-test-gpu.txt'

# Check on macOS (~10 seconds later)  
cat ~/eon/nt/sync-test-gpu.txt
```

## 🎯 SAGE Development Workflow

### Phase 0 Execution (GPU Workstation):
```bash
ssh zerotier-remote
cd ~/eon/nt/
export PATH=~/.npm-global/bin:$PATH

# Start Claude Code development session
claude

# Now you can:
# 1. Access all SAGE models (AlphaForge, catch22, tsfresh, TiRex)
# 2. Use RTX 4090 for TiRex inference  
# 3. Get AI assistance from Claude Code
# 4. All changes sync back to macOS automatically
```

### Development Commands:
```bash
# Check GPU status
nvidia-smi

# Install TiRex (with GPU support)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install transformers

# Test TiRex with CUDA
python -c "
import torch
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')
"
```

## 🔧 Troubleshooting

### If Claude Code doesn't start:
```bash
# Check PATH
echo $PATH | grep npm-global

# Add to current session
export PATH=~/.npm-global/bin:$PATH

# Verify installation
claude --version
```

### If sync is slow:
```bash
# Check Syncthing status
curl -s http://localhost:8384/rest/system/status

# Check sync folder status
curl -s http://localhost:8384/rest/db/status?folder=nt-workspace
```

### If remote connection issues:
```bash
# Check ZeroTier peer status
sudo zerotier-cli peers | grep 8f53f201b7

# Test basic connectivity
ping -c 3 172.25.253.142
```

## ✅ Benefits of This Setup

### Development Experience:
- ✅ **Full AI assistance** on the machine with GPU access
- ✅ **Real-time model testing** without network delays
- ✅ **Automatic backup** to macOS via Syncthing
- ✅ **Seamless workspace switching** between machines

### Performance:
- ✅ **Zero latency** for GPU computations  
- ✅ **Local development** with full system access
- ✅ **Background sync** doesn't interrupt workflow
- ✅ **Optimal resource utilization** (GPU where needed)

### Reliability:
- ✅ **Dual workspace backup** (macOS + GPU workstation)
- ✅ **Conflict resolution** via Syncthing versioning  
- ✅ **Recovery options** if one machine fails
- ✅ **Complete audit trail** of all changes

---

**Status**: Ready for bidirectional development workflow  
**Primary Environment**: GPU workstation with Claude Code  
**Backup Environment**: macOS with automatic sync  
**Sync Direction**: Both directions, automatic, ~10-second delay