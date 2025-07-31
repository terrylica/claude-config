#!/bin/bash
# ZeroTier Network & Connectivity Diagnostics
# Part of SAGE Aliases Tool - /Users/terryli/.claude/tools/sage-aliases/

# =============================================================================
# ZEROTIER STATUS & MONITORING
# =============================================================================

# Basic ZeroTier status
alias zt-status='sudo zerotier-cli status && sudo zerotier-cli listnetworks'
alias zt-info='sudo zerotier-cli info -j | jq "{nodeId: .config.nodeId, version: .version, online: .online}"'
alias zt-networks='sudo zerotier-cli listnetworks -j | jq ".[] | {networkId: .networkId, name: .name, status: .status, type: .type}"'

# Peer connection analysis
alias zt-peers='sudo zerotier-cli peers | grep -E "(LEAF|DIRECT|RELAY)"'
alias zt-gpu='sudo zerotier-cli peers | grep 8f53f201b7'
alias zt-connections='sudo zerotier-cli peers | grep -E "(DIRECT|RELAY)" | wc -l | xargs echo "Active connections:"'

# =============================================================================
# CONNECTION QUALITY ANALYSIS
# =============================================================================

# Latency testing
alias zt-ping='ping -c 5 172.25.253.142'
alias zt-ping-continuous='ping 172.25.253.142'
alias zt-latency='ping -c 10 172.25.253.142 | grep "round-trip" | awk -F"/" "{print \"Average latency: \" \$5 \" ms\"}"'

# Connection type verification
alias zt-direct='sudo zerotier-cli peers | grep 8f53f201b7 | grep DIRECT && echo "✅ DIRECT connection active" || echo "⚠️  Using RELAY connection"'
alias zt-performance='echo "📊 ZeroTier Performance Analysis:" && zt-direct && zt-latency'

# =============================================================================
# CONNECTIVITY TESTING
# =============================================================================

# Basic connectivity tests
alias net-check='ping -c 3 172.25.253.142 && echo "✅ GPU workstation reachable"'
alias net-speed='time ssh zerotier-remote "echo \"Speed test\"" && echo "SSH response time measured above"'

# Service connectivity
alias ssh-test='ssh -o ConnectTimeout=5 zerotier-remote "echo \"SSH connectivity confirmed\""'
alias http-test='curl -s --connect-timeout 5 http://172.25.253.142:8384 > /dev/null && echo "✅ Syncthing web interface reachable" || echo "❌ Syncthing not accessible"'

# =============================================================================
# TROUBLESHOOTING & DIAGNOSTICS
# =============================================================================

# Common issue diagnosis
alias net-diagnose='echo "🔍 Network Diagnostic Report

=== ZeroTier Status ===
$(zt-status | head -2)

=== Connection Type ===
$(zt-direct)

=== Connectivity Test ===
$(ping -c 1 172.25.253.142 > /dev/null 2>&1 && echo "✅ Basic connectivity OK" || echo "❌ Connectivity failed")

=== SSH Access ===
$(ssh -o ConnectTimeout=5 zerotier-remote "echo SSH OK" 2>/dev/null || echo "❌ SSH failed")

=== Performance ===
$(zt-latency 2>/dev/null || echo "Latency test failed")

Diagnostic Complete ✅"'

# Network quality watch
alias net-watch='watch -n 5 "echo \"ZeroTier Status:\" && sudo zerotier-cli peers | grep 8f53f201b7 && echo \"\" && echo \"Connectivity:\" && ping -c 1 172.25.253.142 | grep time="'