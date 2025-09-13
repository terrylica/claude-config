#!/bin/bash
# CNS Remote Alert System - Comprehensive Testing Script
# Tests both SSH tunnel and fallback notification methods

set -e

echo "🧪 CNS Remote Alert System - End-to-End Testing"
echo "=============================================="
echo ""

# Test results tracking
TESTS_PASSED=0
TESTS_TOTAL=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -n "Testing $test_name... "
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo "✅ PASS"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo "❌ FAIL"
        return 1
    fi
}

echo "📋 Environment Checks"
echo "-------------------"

# Check if we're in SSH session
if [[ -n "${SSH_CLIENT:-}" ]]; then
    echo "✅ SSH session detected (SSH_CLIENT: $SSH_CLIENT)"
else
    echo "❌ Not in SSH session - testing local fallback only"
fi

# Check hostname
echo "🖥️  Current hostname: $(hostname)"
echo "📁 Current directory: $(pwd)"
echo ""

echo "🔧 Component Tests" 
echo "----------------"

# Test 1: Remote client exists and is executable
run_test "Remote client availability" "[[ -x ~/.claude/tools/cns-remote-client.sh ]]"

# Test 2: Remote-aware hook exists and is executable  
run_test "Remote-aware hook availability" "[[ -x ~/.claude/tools/cns_hook_entry_remote.sh ]]"

# Test 3: SSH tunnel port availability (client side)
run_test "SSH tunnel port reachable" "nc -z 127.0.0.1 4000 -w 2"

# Test 4: Original CNS system availability
run_test "Original CNS system present" "[[ -f ~/.claude/automation/cns/conversation_handler.sh ]]"

echo ""
echo "📡 Network Connectivity Tests"
echo "----------------------------"

# Test 5: Internet connectivity for fallback services
run_test "Internet connectivity" "curl -s --connect-timeout 3 https://httpbin.org/status/200"

# Test 6: Pushover API reachability
run_test "Pushover API reachable" "curl -s --connect-timeout 3 https://api.pushover.net/1/messages.json"

# Test 7: ntfy service reachability  
run_test "ntfy service reachable" "curl -s --connect-timeout 3 https://ntfy.sh"

echo ""
echo "🎯 Notification Delivery Tests"
echo "-----------------------------"

# Test 8: Remote client basic functionality
if run_test "Remote client basic test" "~/.claude/tools/cns-remote-client.sh --test"; then
    echo "   📱 Check your local macOS or mobile device for test notification"
fi

# Test 9: JSON payload handling
test_json='{"user_prompt":"Test prompt","claude_response":"Test response from automated testing"}'
if run_test "JSON payload handling" "echo '$test_json' | ~/.claude/tools/cns-remote-client.sh"; then
    echo "   📱 Check for JSON-formatted test notification"
fi

# Test 10: Hook integration simulation
if run_test "Hook integration test" "~/.claude/tools/cns-remote-client.sh --hook 'Test user input' 'Test Claude response from hook integration'"; then
    echo "   📱 Check for hook-formatted test notification"  
fi

echo ""
echo "📊 Test Results Summary"
echo "====================="
echo "Tests passed: $TESTS_PASSED/$TESTS_TOTAL"

if [[ $TESTS_PASSED -eq $TESTS_TOTAL ]]; then
    echo "🎉 All tests passed! CNS Remote system is ready."
elif [[ $TESTS_PASSED -ge $((TESTS_TOTAL * 3 / 4)) ]]; then
    echo "⚠️  Most tests passed. Check failed tests above."
else
    echo "❌ Multiple test failures. Review configuration."
fi

echo ""
echo "🎯 Next Steps for Full Deployment"
echo "================================"

if [[ -n "${SSH_CLIENT:-}" ]]; then
    echo "You are currently SSH'd into this Linux box from $(echo $SSH_CLIENT | cut -d' ' -f1)"
    echo ""
    echo "On your LOCAL macOS machine ($(echo $SSH_CLIENT | cut -d' ' -f1)), run:"
    echo "1. scp kab:~/.claude/tools/cns-local-hub.py ~/.claude/tools/"
    echo "2. scp kab:~/.claude/tools/macos-setup.sh ~/.claude/tools/"  
    echo "3. ~/.claude/tools/macos-setup.sh"
    echo "4. ssh -f -N kab  # Start SSH tunnel"
    echo "5. ~/.claude/tools/start-cns-hub.sh  # Start notification hub"
    echo ""
    echo "Then test full system:"
    echo "6. From this Linux session: ~/.claude/tools/cns-remote-client.sh 'Full system test!'"
fi

echo ""
echo "🔧 Configuration Options"
echo "======================="
echo "• Pushover fallback: ~/.claude/tools/setup-pushover-fallback.sh"
echo "• Deploy remote-aware hooks: ~/.claude/tools/deploy-remote-cns.sh"
echo "• View logs: tail -f /tmp/claude_cns_debug.log"
echo "• Remote client help: ~/.claude/tools/cns-remote-client.sh --help"