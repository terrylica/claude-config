# GPU-as-a-Service: Solutions for macOS + Remote RTX 4090

## Solution 1: SSH + Jupyter Tunneling (RECOMMENDED)

### Architecture
```
macOS (Your Development)          Remote GPU Workstation
├── Claude Code ✅               ├── Jupyter Server (GPU kernels)
├── Local Python env ✅          ├── TiRex + PyTorch CUDA ✅
├── Data analysis ✅             ├── Heavy GPU computations
├── Feature engineering ✅       └── Results → sync back
└── SSH tunnel ↔ Port 8888 ←────────┘
```

### Setup (5 minutes)

#### On GPU Workstation (one-time setup):
```bash
ssh zerotier-remote
pip install jupyter torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install transformers tirex
jupyter notebook --generate-config
# Edit config to allow remote connections
jupyter notebook --port=8888 --no-browser --allow-root
```

#### On macOS (daily usage):
```bash
# Create SSH tunnel
ssh -L 8888:localhost:8888 zerotier-remote -N &

# Open in browser: http://localhost:8888
# Now you have GPU access in Jupyter on your Mac!
```

### Advantages
✅ **Keep Claude Code on macOS** - Full local development experience  
✅ **Minimal setup** - Just SSH tunneling  
✅ **Real-time GPU access** - Run cells with RTX 4090 power  
✅ **Visual interface** - Jupyter notebooks for experimentation  
✅ **File sync** - Easy copy/paste between local and remote  

## Solution 2: PyTorch Remote RPC (INTERMEDIATE)

### Architecture
```python
# On macOS - your local code
import torch.distributed.rpc as rpc

# Initialize RPC to GPU workstation
rpc.init_rpc("client", rank=0, world_size=2, 
             rpc_backend_options=rpc.TensorPipeRpcBackendOptions(
                 init_method="tcp://172.25.253.142:29500"))

# Run TiRex remotely with local data
future = rpc.rpc_async("gpu_worker", tirex_inference, args=(data,))
result = future.wait()  # Get results back to macOS
```

### Setup
- Install PyTorch with distributed support on both machines
- Configure RPC worker on GPU workstation
- Write simple wrapper functions for TiRex calls

### Advantages
✅ **Pure Python solution** - No complex tooling  
✅ **Transparent remote calls** - Feels like local execution  
✅ **Good performance** - Optimized tensor transfer  

## Solution 3: SCUDA - GPU Over IP (ADVANCED)

### Architecture
- Install SCUDA client on macOS
- Install SCUDA server on GPU workstation  
- Route CUDA calls over network transparently

### Reality Check
⚠️ **Experimental technology** - May have stability issues  
⚠️ **Complex setup** - Requires CUDA toolkit compilation  
⚠️ **Network overhead** - Performance may be inconsistent  

## RECOMMENDED IMPLEMENTATION PLAN

### Phase 1: Jupyter Tunneling (Today - 15 minutes)
```bash
# 1. Setup GPU workstation Jupyter
ssh zerotier-remote "pip install jupyter torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121"

# 2. Start Jupyter on GPU workstation
ssh zerotier-remote "nohup jupyter notebook --port=8888 --no-browser --ip=0.0.0.0 --allow-root > jupyter.log 2>&1 &"

# 3. Create tunnel on macOS
ssh -L 8888:localhost:8888 zerotier-remote -N &

# 4. Open http://localhost:8888 in your browser
```

### Phase 2: TiRex Integration (Tomorrow)
Create GPU workstation notebook:
```python
# In Jupyter on GPU workstation
import torch
from tirex import load_model
import pandas as pd

# Load your BTCUSDT data
data = pd.read_parquet('/path/to/btcusdt_data.parquet')

# Load TiRex with GPU
model = load_model("NX-AI/TiRex")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"GPU: {torch.cuda.get_device_name(0)}")

# Run forecasting
forecast = model.forecast(context=torch_data, prediction_length=64)
```

### Phase 3: Automated Workflow (Next Week)
```bash
# Create GPU computation scripts
# Sync data: macOS → GPU workstation  
# Run computation: GPU workstation
# Sync results: GPU workstation → macOS
```

## Quick Start Commands

### Create Aliases for GPU Cloud
```bash
# Add to ~/.claude/gpu-workstation-aliases.sh
alias gpu-jupyter='ssh -L 8888:localhost:8888 zerotier-remote -N &'
alias gpu-tunnel-status='ps aux | grep "ssh.*8888" | grep -v grep'
alias gpu-sync-data='rsync -avz ~/eon/nt/data_cache/ zerotier-remote:~/gpu_data/'
alias gpu-sync-results='rsync -avz zerotier-remote:~/gpu_results/ ~/eon/nt/gpu_results/'

# Start GPU cloud session
gpu-jupyter
open http://localhost:8888
```

## Performance Expectations

### Jupyter Tunneling
- **Latency**: ~10-20ms for notebook interactions
- **Throughput**: Full GPU bandwidth for computations
- **Use case**: Suitable for TiRex inference, model training
- **Data transfer**: Only results transferred, not full datasets

### Bandwidth Usage
- **Code execution**: Minimal (few KB)
- **Data visualization**: Moderate (plots/charts)
- **Model weights**: One-time download to GPU workstation
- **Results**: Small (predictions, metrics)

## Integration with SAGE Workflow

### Local Development (macOS)
```python
# In your local Claude Code environment
import pandas as pd
from sage.feature_extraction import extract_catch22, extract_tsfresh

# Extract features locally (CPU-friendly)
btcusdt_data = pd.read_parquet('data_cache/BTCUSDT_validated_market_data.parquet')
catch22_features = extract_catch22(btcusdt_data)
tsfresh_features = extract_tsfresh(btcusdt_data)

# Save for GPU processing
features = pd.concat([catch22_features, tsfresh_features], axis=1)
features.to_parquet('features_for_gpu.parquet')
```

### GPU Processing (Remote Jupyter)
```python
# In GPU workstation Jupyter notebook
import torch
from tirex import load_model

# Load features from macOS
features = pd.read_parquet('features_for_gpu.parquet')

# Run TiRex with uncertainty quantification
model = load_model("NX-AI/TiRex")
predictions = model.forecast(features, prediction_length=24)
uncertainty = model.get_uncertainty(features)

# Save results for macOS
results = pd.DataFrame({
    'predictions': predictions,
    'uncertainty': uncertainty
})
results.to_parquet('tirex_results.parquet')
```

### Back to Local (macOS)
```python
# Download and integrate results
gpu_results = pd.read_parquet('gpu_results/tirex_results.parquet')

# Continue with SAGE ensemble integration
sage_predictions = ensemble_combine(
    alphaforge_signals,
    catch22_features, 
    tsfresh_features,
    gpu_results['predictions'],
    uncertainty_weights=gpu_results['uncertainty']
)
```

---

**Status**: Ready for immediate implementation  
**Recommended**: Start with Jupyter tunneling (15-minute setup)  
**Next**: TiRex integration for SAGE Phase 0 validation