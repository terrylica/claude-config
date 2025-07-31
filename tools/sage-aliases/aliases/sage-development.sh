#!/bin/bash
# SAGE Development Specific Aliases
# Part of SAGE Aliases Tool - /Users/terryli/.claude/tools/sage-aliases/

# =============================================================================
# SAGE SESSION SAFETY
# =============================================================================

# Safe session startup with corruption prevention
function sage-safe-start() {
    # Check for active sessions on other machines
    if test -f ~/.claude/.session-owner; then
        echo "⚠️  Session active on: $(cat ~/.claude/.session-owner)"
        return 1
    fi
    
    # Check for sync conflicts
    if ls ~/.claude/projects/*.sync-conflict* 2>/dev/null; then
        echo "🚨 Resolve sync conflicts first: ls ~/.claude/projects/*.sync-conflict*"
        return 1
    fi
    
    # Validate session file integrity
    if ! find ~/.claude/projects -name "*.jsonl" -exec jq empty {} \; 2>/dev/null; then
        echo "🚨 Corrupted session file detected - check ~/.claude/projects/"
        return 1
    fi
    
    # Create session lock
    echo "$(hostname)-$(date)" > ~/.claude/.session-owner
    trap 'rm -f ~/.claude/.session-owner' EXIT
    echo "✅ Session safety checks passed"
}

# =============================================================================
# SAGE MODEL ALIASES
# =============================================================================

# Individual model development (with session safety)
alias alphaforge-dev='sage-safe-start && cd ~/eon/nt/repos/alphaforge && echo "📊 AlphaForge Development" && claude'
alias catch22-dev='sage-safe-start && cd ~/eon/nt && echo "🎣 catch22 Features Development" && python3 -c "import pycatch22; print(f\"catch22 version: {pycatch22.__version__}\")" && claude'
alias tsfresh-dev='sage-safe-start && cd ~/eon/nt && echo "🔍 tsfresh Features Development" && python3 -c "import tsfresh; print(f\"tsfresh version: {tsfresh.__version__}\")" && claude'
alias tirex-gpu='ssh zerotier-remote -t "sage-safe-start && cd ~/eon/nt && echo \"🦕 TiRex GPU Development\" && export PATH=~/.npm-global/bin:\$PATH && python3 -c \"import torch; print(f\\\"CUDA: {torch.cuda.is_available()}, Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \\\"None\\\"}\\\")\" && claude"'

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