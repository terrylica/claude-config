#!/bin/bash
# GPU Workstation Connection & Management Aliases
# Part of SAGE Aliases Tool - ~/.claude/tools/sage-aliases/

# =============================================================================
# QUICK CONNECTION ALIASES
# =============================================================================

# Basic connections
alias gpu='ssh zerotier-remote'
alias gpu-tmux='ssh zerotier-remote -t "tmux new-session -A -s dev"'
alias gpu-resume='ssh zerotier-remote -t "tmux attach -t dev"'

# Development sessions
alias gpu-claude='ssh zerotier-remote -t "cd ~/eon/nt && export PATH=~/.npm-global/bin:\$PATH && claude"'
alias gpu-sage='ssh zerotier-remote -t "cd ~/eon/nt && echo \"SAGE Development - GPU Environment (RTX 4090)\" && export PATH=~/.npm-global/bin:\$PATH && nvidia-smi --query-gpu=gpu_name,memory.used,memory.total --format=csv,noheader,nounits && claude"'

# =============================================================================
# SYSTEM STATUS & MONITORING
# =============================================================================

# GPU monitoring
alias gpu-status='ssh zerotier-remote "hostname && nvidia-smi --query-gpu=gpu_name,memory.used,memory.total --format=csv,noheader,nounits"'
alias gpu-memory='ssh zerotier-remote "nvidia-smi --query-gpu=memory.used,memory.total,memory.free --format=csv,noheader,nounits"'
alias gpu-processes='ssh zerotier-remote "nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv,noheader"'
alias gpu-temp='ssh zerotier-remote "nvidia-smi --query-gpu=temperature.gpu,power.draw,utilization.gpu --format=csv,noheader,nounits"'

# System monitoring
alias gpu-uptime='ssh zerotier-remote "uptime && free -h && df -h ~"'
alias gpu-load='ssh zerotier-remote "cat /proc/loadavg && vmstat 1 3"'
alias gpu-disk='ssh zerotier-remote "df -h && du -sh ~/eon/nt"'

# Development environment status
alias gpu-env='ssh zerotier-remote "echo \"=== Development Environment Status ===\" && node --version && export PATH=~/.npm-global/bin:\$PATH && claude --version && python3 --version && echo \"CUDA Available:\" && python3 -c \"import torch; print(torch.cuda.is_available())\" 2>/dev/null || echo \"PyTorch not installed\""'

# =============================================================================
# NETWORK & CONNECTIVITY
# =============================================================================

# Connection testing
alias gpu-ping='ping -c 3 172.25.253.142'
alias gpu-check='ping -c 2 172.25.253.142 && echo "✅ GPU workstation reachable"'
alias gpu-speed='time ssh zerotier-remote "echo \"Connection speed test\""'

# Network diagnostics
alias gpu-network='ssh zerotier-remote "ip addr show | grep inet && ss -tuln | grep :22"'
alias gpu-zerotier='ssh zerotier-remote "sudo zerotier-cli status && sudo zerotier-cli listnetworks"'

# =============================================================================
# DEVELOPMENT SHORTCUTS
# =============================================================================

# Quick development actions
alias gpu-pull='ssh zerotier-remote "cd ~/eon/nt && git pull origin master"'
alias gpu-status-git='ssh zerotier-remote "cd ~/eon/nt && git status --porcelain"'
alias gpu-jupyter='ssh zerotier-remote -L 8888:localhost:8888 "cd ~/eon/nt && jupyter lab --no-browser --port=8888"'

# Python environment
alias gpu-python='ssh zerotier-remote -t "cd ~/eon/nt && python3"'
alias gpu-pip='ssh zerotier-remote "cd ~/eon/nt && pip3 list | grep -E \"torch|numpy|pandas|transformers\""'

# =============================================================================
# COMPOSITE WORKFLOWS
# =============================================================================

# Complete development startup
alias gpu-dev='echo "🚀 Starting GPU development session..." && gpu-check && gpu-status && gpu-claude'

# Full system check
alias gpu-health='echo "🔍 GPU Workstation Health Check..." && gpu-check && gpu-status && gpu-env && echo "✅ Health check complete"'

# SAGE development with monitoring
alias sage-gpu-monitor='ssh zerotier-remote -t "
echo \"=== SAGE GPU Development Session ===\"
echo \"GPU Status:\"
nvidia-smi --query-gpu=gpu_name,memory.used,memory.total --format=csv,noheader,nounits
echo \"Environment:\"
cd ~/eon/nt
export PATH=~/.npm-global/bin:\$PATH
echo \"Node.js: \$(node --version)\"
echo \"Claude Code: \$(claude --version)\"
echo \"Python: \$(python3 --version)\"
echo \"PyTorch CUDA: \$(python3 -c \\\"import torch; print(torch.cuda.is_available())\\\" 2>/dev/null || echo \\\"Not available\\\")\"
echo \"Starting development session...\"
claude
"'