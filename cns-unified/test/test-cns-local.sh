#!/bin/bash
# CNS Local Test Script - macOS Local Machine
# Test CNS notification system components

set -e

echo "🧪 CNS Local Test Suite - macOS"
echo "================================"

# Test 1: Check SSH tunnel
echo "1. Testing SSH tunnel to kab host..."
if ssh -O check kab &> /dev/null; then
    echo "   ✅ SSH tunnel active"
else
    echo "   ❌ SSH tunnel not active. Run: ssh -f -N kab"
    exit 1
fi

# Test 2: Check CNS local hub
echo "2. Testing CNS local hub endpoint..."
response=$(curl -s -X POST -d '{"title":"Test Script","message":"CNS test from script"}' \
    -H "Content-Type: application/json" \
    http://127.0.0.1:5050/notify)

if [[ "$response" == *"success"* ]]; then
    echo "   ✅ CNS local hub responding"
else
    echo "   ❌ CNS local hub not responding"
    exit 1
fi

# Test 3: Direct notification tools
echo "3. Testing notification tools..."
terminal-notifier -title "CNS Test Suite" -message "Direct terminal-notifier test" -sound default
echo "   ✅ terminal-notifier tested"

osascript -e 'display notification "Direct osascript test" with title "CNS Test Suite"'
echo "   ✅ osascript tested"

echo ""
echo "🎉 All CNS local components working!"
echo ""
echo "📋 Status Summary:"
echo "   • SSH tunnel: Active (kab host)"
echo "   • CNS local hub: Running on 127.0.0.1:5050"
echo "   • Notifications: terminal-notifier + osascript"
echo "   • Ready for remote Linux notifications"
echo ""
echo "🔗 To test from Linux session on kab host:"
echo "   curl -X POST -d '{\"title\":\"Remote Test\",\"message\":\"From Linux\"}' \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     http://127.0.0.1:4000/notify"