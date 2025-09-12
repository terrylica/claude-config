#!/bin/bash
# Pushover API Integration Setup for CNS Remote Fallback
# Based on agent research: $4.99 one-time, excellent reliability

set -e

echo "📱 CNS Pushover Integration Setup"
echo "================================"
echo ""
echo "Pushover provides reliable push notifications as fallback when SSH tunnel fails."
echo "Cost: \$4.99 one-time (per platform - iOS/Android)"
echo ""

# Check if Pushover is already configured
if [[ -f ~/.pushover_config ]]; then
    echo "✅ Pushover already configured"
    source ~/.pushover_config
    echo "   User Key: ${PUSHOVER_USER:0:8}..."
    echo "   Token: ${PUSHOVER_TOKEN:0:8}..."
    echo ""
    echo "Run with --reconfigure to update settings"
    
    if [[ "$1" != "--reconfigure" ]]; then
        echo ""
        echo "🧪 Testing current configuration..."
        if ~/.claude/tools/cns-remote-client.sh --test; then
            echo "✅ Test notification sent successfully!"
        else
            echo "❌ Test failed. Check configuration or run with --reconfigure"
        fi
        exit 0
    fi
fi

echo "📋 Setup Steps:"
echo "1. Download Pushover app (\$4.99):"
echo "   • iOS: https://apps.apple.com/app/pushover-notifications/id506088175"
echo "   • Android: https://play.google.com/store/apps/details?id=net.superblock.pushover"
echo ""
echo "2. Create account at https://pushover.net"
echo ""
echo "3. Get your User Key from: https://pushover.net"
echo ""
echo "4. Create application at: https://pushover.net/apps/build"
echo "   • Name: CNS Remote Alerts"
echo "   • Description: Claude Code remote notifications"
echo "   • URL: (leave blank)"
echo "   • Icon: (optional)"
echo ""

# Interactive setup
echo "Ready to configure Pushover? (y/n)"
read -r response

if [[ "$response" != "y" && "$response" != "Y" ]]; then
    echo "Setup cancelled. Run this script again when ready."
    exit 0
fi

echo ""
echo "🔑 Enter your Pushover credentials:"
echo ""

# Get User Key
while true; do
    echo -n "User Key (30 characters, from https://pushover.net): "
    read -r user_key
    
    if [[ ${#user_key} -eq 30 && "$user_key" =~ ^[a-zA-Z0-9]+$ ]]; then
        break
    else
        echo "❌ Invalid User Key. Should be 30 alphanumeric characters."
    fi
done

# Get Application Token  
while true; do
    echo -n "Application Token (30 characters, from your app): "
    read -r app_token
    
    if [[ ${#app_token} -eq 30 && "$app_token" =~ ^[a-zA-Z0-9]+$ ]]; then
        break
    else
        echo "❌ Invalid Application Token. Should be 30 alphanumeric characters."
    fi
done

# Save configuration
cat > ~/.pushover_config << EOF
# Pushover Configuration for CNS Remote Fallback
# Generated: $(date)
PUSHOVER_USER="$user_key"
PUSHOVER_TOKEN="$app_token"
EOF

chmod 600 ~/.pushover_config

echo ""
echo "✅ Pushover configuration saved!"
echo ""

# Test the configuration
echo "🧪 Testing configuration..."

if curl -s --connect-timeout 10 \
    -F "token=$app_token" \
    -F "user=$user_key" \
    -F "message=CNS Remote Setup Test - Configuration successful!" \
    -F "title=CNS Remote Alert" \
    -F "priority=0" \
    https://api.pushover.net/1/messages.json | grep -q '"status":1'; then
    
    echo "✅ Test notification sent successfully!"
    echo "   Check your phone for the test notification"
    echo ""
    echo "🎯 Pushover fallback is now ready!"
    echo "   When SSH tunnel fails, notifications will use Pushover"
    
else
    echo "❌ Test failed. Please check:"
    echo "   • Internet connection"  
    echo "   • User Key and Application Token"
    echo "   • Pushover service status"
    echo ""
    echo "You can reconfigure with: $0 --reconfigure"
fi

echo ""
echo "📖 Usage:"
echo "   • SSH tunnel working: Notifications go to macOS"
echo "   • SSH tunnel fails: Notifications go to Pushover app"
echo "   • Manual test: ~/.claude/tools/cns-remote-client.sh --test"