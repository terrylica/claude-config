#!/bin/bash
# Syncthing & Synchronization Monitoring Aliases
# Part of SAGE Aliases Tool - ~/.claude/tools/sage-aliases/

# =============================================================================
# SYNC STATUS MONITORING
# =============================================================================

# Basic sync status
alias sync-status='curl -s http://localhost:8384/rest/system/status | jq -r .myID && echo "Sync service running"'
alias sync-health='curl -s http://localhost:8384/rest/db/status?folder=nt-workspace | jq -r .state'
alias sync-errors='curl -s http://localhost:8384/rest/db/status?folder=nt-workspace | jq -r .errors'

# Detailed sync information
alias sync-info='curl -s http://localhost:8384/rest/system/status | jq "{myID: .myID, cpuPercent: .cpuPercent, uptime: .uptime}"'
alias sync-folder='curl -s http://localhost:8384/rest/db/status?folder=nt-workspace | jq "{needFiles: .needFiles, state: .state, errors: .errors, globalBytes: .globalBytes, localBytes: .localBytes}"'

# Connection status
alias sync-connections='curl -s http://localhost:8384/rest/system/connections | jq ".connections"'
alias sync-gpu-connection='curl -s http://localhost:8384/rest/system/connections | jq ".connections[\"ZOYKTSR-YBGYP7D-MZHE6RN-SMXZESR-V3QMNKZ-B3CJJIO-KJV5MR4-LIQM3AH\"]"'

# =============================================================================
# SYNC TESTING & VERIFICATION
# =============================================================================

# Sync test workflow
alias sync-test='echo "🔄 Testing bidirectional sync..." && 
echo "Test from macOS $(date)" > ~/eon/nt/sync-test-mac.txt &&
echo "⏱️  Waiting 12 seconds for sync..." &&
sleep 12 &&
echo "Remote content:" &&
ssh zerotier-remote "cat ~/eon/nt/sync-test-mac.txt 2>/dev/null || echo \"Sync failed - file not found\""'

alias sync-test-reverse='echo "🔄 Testing reverse sync..." &&
ssh zerotier-remote "echo \"Test from GPU $(date)\" > ~/eon/nt/sync-test-gpu.txt" &&
echo "⏱️  Waiting 12 seconds for sync..." &&
sleep 12 &&
echo "Local content:" &&
cat ~/eon/nt/sync-test-gpu.txt 2>/dev/null || echo "Reverse sync failed - file not found"'

# Comprehensive sync verification
alias sync-verify='echo "🔍 Comprehensive sync verification:

=== Local Files ===" &&
ls -la ~/eon/nt/ | head -5 &&
echo "
=== Remote Files ===" &&
ssh zerotier-remote "ls -la ~/eon/nt/" | head -5 &&
echo "
=== Sync Status ===" &&
sync-health &&
echo "
=== Connection Status ===" &&
curl -s http://localhost:8384/rest/system/connections | jq ".connections[\"ZOYKTSR-YBGYP7D-MZHE6RN-SMXZESR-V3QMNKZ-B3CJJIO-KJV5MR4-LIQM3AH\"].connected"'

# =============================================================================
# SYNC OPERATIONS
# =============================================================================

# Force operations
alias sync-scan='curl -X POST http://localhost:8384/rest/db/scan?folder=nt-workspace && echo "Forced folder scan initiated"'
alias sync-restart='curl -X POST http://localhost:8384/rest/system/restart && echo "Syncthing restart initiated"'

# =============================================================================
# COMPREHENSIVE HEALTH CHECK
# =============================================================================

alias sync-health-full='echo "🏥 Comprehensive Sync Health Check

=== Service Status ===
Local: $(brew services list | grep syncthing | awk "{print \$2}")  
Remote: $(ssh zerotier-remote "pgrep syncthing > /dev/null && echo \"Running\" || echo \"Stopped\"")

=== Sync Status ===
Folder State: $(sync-health)
Errors: $(sync-errors)

=== Connection Status ===  
GPU Workstation: $(curl -s http://localhost:8384/rest/system/connections | jq -r ".connections[\"ZOYKTSR-YBGYP7D-MZHE6RN-SMXZESR-V3QMNKZ-B3CJJIO-KJV5MR4-LIQM3AH\"].connected")

=== Performance ===
Last Completion: $(curl -s http://localhost:8384/rest/db/status?folder=nt-workspace | jq -r .stateChanged)

Health Check Complete ✅"'