#!/bin/bash
# SAGE Development Specific Aliases
# Part of SAGE Aliases Tool - ~/.claude/tools/sage-aliases/

# =============================================================================
# CLAUDE SESSION SYNC (Simple Git-Based)
# =============================================================================

# Simple Claude session backup/restore
function claude-session-backup() {
    cd ~/.claude && git add projects/ && git commit -m "session backup: $(hostname) $(date '+%H:%M')" && git push
    echo "✅ Claude sessions backed up"
}

function claude-session-restore() {
    cd ~/.claude && git pull
    echo "✅ Claude sessions restored"
}

# =============================================================================
# SAGE MODEL ALIASES
# =============================================================================

# Individual model development (simplified)
alias alphaforge-dev='cd ~/eon/nt/repos/alphaforge && claude'
alias catch22-dev='cd ~/eon/nt && claude'  
alias tsfresh-dev='cd ~/eon/nt && claude'
alias tirex-gpu='ssh zerotier-remote -t "cd ~/eon/nt && claude"'

# =============================================================================
# SAGE ENSEMBLE DEVELOPMENT
# =============================================================================

# Complete SAGE framework
alias sage-ensemble='ssh zerotier-remote -t "
cd ~/eon/nt
echo \"🧠 SAGE Ensemble Development Session\"
export PATH=~/.npm-global/bin:\$PATH
echo \"=== Model Availability Check ===\"
echo \"✅ AlphaForge: \$(ls repos/alphaforge/ | head -3)\"
python3 -c \"import pycatch22; print(\\\"✅ catch22: Available\\\")\" 2>/dev/null || echo \"❌ catch22: Not available\"
python3 -c \"import tsfresh; print(\\\"✅ tsfresh: Available\\\")\" 2>/dev/null || echo \"❌ tsfresh: Not available\"
python3 -c \"import torch; print(f\\\"✅ TiRex GPU: {torch.cuda.is_available()}\\\")\" 2>/dev/null || echo \"❌ TiRex: PyTorch not available\"
echo \"=== Starting SAGE Development ===\"
claude
"'

# SAGE validation workflow
alias sage-validate='ssh zerotier-remote -t "
cd ~/eon/nt
echo \"🔬 SAGE Model Validation Workflow\"  
export PATH=~/.npm-global/bin:\$PATH
echo \"Models ready for validation:\"
echo \"  📊 AlphaForge (formulaic alpha factors)\"
echo \"  🎣 catch22 (canonical time series features)\"
echo \"  🔍 tsfresh (automated feature selection)\"
echo \"  🦕 TiRex (GPU-accelerated forecasting)\"
claude
"'

# =============================================================================
# TASK-ORIENTED DEVELOPMENT
# =============================================================================

# Auto-select optimal environment based on task
function sage_development() {
    local task=$1
    case $task in
        "docs"|"documentation"|"planning"|"research")
            echo "📚 Using macOS for documentation work"
            cd ~/eon/nt/docs && claude
            ;;
        "tirex"|"gpu"|"inference"|"training")
            echo "🎮 Using GPU workstation for compute-intensive work"
            ssh zerotier-remote -t "cd ~/eon/nt && export PATH=~/.npm-global/bin:\$PATH && claude"
            ;;
        "ensemble"|"sage"|"integration"|"all")
            echo "🧠 Using GPU workstation for full SAGE integration"
            sage-ensemble
            ;;
        "local"|"cpu"|"testing")
            echo "🍎 Using macOS for local development"
            cd ~/eon/nt && claude
            ;;
        *)
            echo "Usage: sage_development [docs|tirex|ensemble|local]
            
Available options:
  docs       - Documentation and planning (macOS)
  tirex      - TiRex GPU inference (GPU workstation)
  ensemble   - Full SAGE integration (GPU workstation)
  local      - Local CPU development (macOS)"
            ;;
    esac
}

# Shorthand for sage_development function
alias sage-dev='sage_development'

# =============================================================================
# MODEL STATUS & DIAGNOSTICS
# =============================================================================

# Model availability check
function models-status() {
    echo "📊 SAGE Models Status:"
    echo ""
    echo "✅ AlphaForge: $(ls ~/eon/nt/repos/alphaforge/ > /dev/null 2>&1 && echo "Available" || echo "Missing")"
    echo "✅ NautilusTrader: $(ls ~/eon/nt/repos/nautilus_trader/ > /dev/null 2>&1 && echo "Available" || echo "Missing")"  
    echo "✅ DSM: $(ls ~/eon/nt/repos/data-source-manager/ > /dev/null 2>&1 && echo "Available" || echo "Missing")"
    echo "✅ FinPlot: $(ls ~/eon/nt/repos/finplot/ > /dev/null 2>&1 && echo "Available" || echo "Missing")"
    echo "✅ catch22: $(python3 -c "import pycatch22; print('Available')" 2>/dev/null || echo "Not installed")"
    echo "✅ tsfresh: $(python3 -c "import tsfresh; print('Available')" 2>/dev/null || echo "Not installed")"
    echo "✅ TiRex GPU: $(ssh zerotier-remote "python3 -c \"import torch; print('Available' if torch.cuda.is_available() else 'CUDA not available')\"" 2>/dev/null || echo "Remote check failed")"
}

# SAGE environment diagnostics
function sage-diag() {
    echo "🔍 SAGE Environment Diagnostics"
    echo ""
    echo "Local macOS:"
    python3 -c "import pycatch22, tsfresh; print(f\"catch22: {pycatch22.__version__}, tsfresh: {tsfresh.__version__}\")" 2>/dev/null || echo "Python packages not available locally"
    echo ""
    echo "Remote GPU:"
    ssh zerotier-remote "python3 -c \"import torch; print(f'PyTorch: {torch.__version__}, CUDA: {torch.cuda.is_available()}')\"" 2>/dev/null || echo "Remote Python environment check failed"
    echo ""
    echo "Repositories:"
    ls -la ~/eon/nt/repos/ | grep -E "(alphaforge|nautilus|data-source|finplot)"
}