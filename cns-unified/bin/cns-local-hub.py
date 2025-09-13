#!/usr/bin/env python3
"""
CNS Local Hub - macOS Notification Server
Receives notifications from remote SSH sessions and triggers local macOS notifications.
Part of the CNS remote alert transmission system.
"""

import json
import logging
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlparse

# Configuration
HUB_HOST = '127.0.0.1'
HUB_PORT = 5050
LOG_FILE = '/tmp/cns-local-hub.log'

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class CNSNotificationHandler(BaseHTTPRequestHandler):
    """HTTP handler for incoming CNS notifications."""
    
    def do_POST(self):
        """Handle POST requests with notification payloads."""
        try:
            # Parse request
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error(400, "Empty request body")
                return
                
            body = self.rfile.read(content_length).decode('utf-8')
            
            # Handle both JSON and plain text notifications
            try:
                notification_data = json.loads(body)
                self._handle_json_notification(notification_data)
            except json.JSONDecodeError:
                # Fallback to plain text notification
                self._handle_text_notification(body.strip())
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "success"}')
            
        except Exception as e:
            logger.error(f"Error handling notification: {e}")
            self.send_error(500, f"Internal server error: {e}")
    
    def do_GET(self):
        """Handle health check requests."""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "healthy", "service": "cns-local-hub"}')
        else:
            self.send_error(404, "Not Found")
    
    def _handle_json_notification(self, data):
        """Process structured JSON notification."""
        logger.info(f"Received JSON notification: {data}")
        
        # Extract notification components
        title = data.get('title', 'CNS Remote Alert')
        message = data.get('message', data.get('content', {}).get('claude_response', 'Remote notification'))
        
        # Add context information if available
        if 'environment' in data:
            env = data['environment']
            hostname = env.get('hostname', 'remote')
            cwd = env.get('cwd', '')
            if cwd:
                message = f"[{hostname}:{cwd}] {message}"
            else:
                message = f"[{hostname}] {message}"
        
        self._send_macos_notification(title, message)
        
        # CRITICAL: Trigger local CNS audio system (toy-story + TTS)
        self._trigger_cns_audio_system(title, message, data)
        
        # Handle clipboard if requested
        if data.get('clipboard_enabled', False):
            clipboard_content = data.get('content', {}).get('claude_response', '')
            if clipboard_content:
                self._update_clipboard(clipboard_content)
    
    def _handle_text_notification(self, text):
        """Process plain text notification."""
        logger.info(f"Received text notification: {text}")
        self._send_macos_notification("CNS Remote Alert", text)
        
        # Try to parse JSON from text to get environment data
        try:
            import json
            data = json.loads(text)
        except:
            data = {}
        
        # CRITICAL: Trigger local CNS audio system (toy-story + TTS)
        self._trigger_cns_audio_system("CNS Remote Alert", text, data)
    
    def _send_macos_notification(self, title, message):
        """Send notification to macOS notification center."""
        try:
            # Try terminal-notifier first (recommended by agents)
            if self._check_command_exists('terminal-notifier'):
                cmd = [
                    'terminal-notifier',
                    '-title', title,
                    '-message', message,
                    '-group', 'cns-remote',
                    '-sound', 'default'
                ]
                subprocess.run(cmd, check=True, timeout=5)
                logger.info(f"Sent notification via terminal-notifier: {title}")
                return
            
            # Fallback to alerter (backup from agent research)
            if self._check_command_exists('alerter'):
                cmd = [
                    'alerter',
                    '-title', title,
                    '-message', message,
                    '-group', 'cns-remote'
                ]
                subprocess.run(cmd, check=True, timeout=5)
                logger.info(f"Sent notification via alerter: {title}")
                return
            
            # Final fallback to osascript (though agents noted issues)
            cmd = [
                'osascript', '-e',
                f'display notification "{message}" with title "{title}"'
            ]
            subprocess.run(cmd, check=True, timeout=5)
            logger.info(f"Sent notification via osascript: {title}")
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to send notification: {e}")
        except subprocess.TimeoutExpired:
            logger.error("Notification command timed out")
        except Exception as e:
            logger.error(f"Unexpected error sending notification: {e}")
    
    def _update_clipboard(self, content):
        """Update macOS clipboard with content."""
        try:
            process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            process.communicate(content.encode('utf-8'))
            if process.returncode == 0:
                logger.info("Updated clipboard with remote content")
            else:
                logger.error("Failed to update clipboard")
        except Exception as e:
            logger.error(f"Error updating clipboard: {e}")
    
    def _check_command_exists(self, command):
        """Check if a command is available in PATH."""
        try:
            subprocess.run(['which', command], check=True, 
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _trigger_cns_audio_system(self, title, message, data=None):
        """Trigger local CNS audio system (toy-story + TTS)."""
        try:
            import json
            import os
            
            # Read volume from CNS config
            config_path = os.path.expanduser("~/.claude/automation/cns/config/cns_config.json")
            volume = 0.3  # default
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    volume = config.get('audio', {}).get('notification_volume', 0.3)
            except:
                pass
            
            # Play toy-story notification FIRST (wait for completion)
            audio_file = os.path.expanduser("~/.claude/media/toy-story-notification.mp3")
            if os.path.exists(audio_file):
                subprocess.run([
                    'afplay', audio_file, '--volume', str(volume)
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
                logger.info(f"Played CNS audio notification at volume {volume}")
            
            # THEN TTS announcement (after toy-story finishes) 
            tts_text = "dot claude"  # default fallback
            if data and isinstance(data, dict):
                # Extract Linux directory from environment data
                linux_cwd = data.get('environment', {}).get('cwd', '')
                if linux_cwd:
                    # Get just the directory name (e.g., "tmp" from "/tmp")
                    dir_name = os.path.basename(linux_cwd.rstrip('/'))
                    if dir_name:
                        tts_text = dir_name
                        logger.info(f"Using Linux directory '{dir_name}' for TTS")
            
            subprocess.Popen([
                'say', tts_text
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"Triggered CNS TTS announcement: '{tts_text}'")
            
        except Exception as e:
            logger.error(f"Error triggering CNS audio system: {e}")
    
    def log_message(self, format, *args):
        """Override to use our logger instead of stderr."""
        logger.info(f"HTTP: {format % args}")


def start_hub_server():
    """Start the CNS notification hub server."""
    try:
        server = HTTPServer((HUB_HOST, HUB_PORT), CNSNotificationHandler)
        logger.info(f"CNS Local Hub started on http://{HUB_HOST}:{HUB_PORT}")
        logger.info(f"Logs available at: {LOG_FILE}")
        logger.info("Ready to receive remote notifications...")
        
        # Check for notification tools
        tools_available = []
        for tool in ['terminal-notifier', 'alerter', 'osascript']:
            if CNSNotificationHandler._check_command_exists(None, tool):
                tools_available.append(tool)
        logger.info(f"Available notification tools: {tools_available}")
        
        server.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("CNS Local Hub stopped by user")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            logger.error(f"Port {HUB_PORT} already in use. Is another hub running?")
        else:
            logger.error(f"Server error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


def install_macos_tools():
    """Check and provide installation instructions for macOS notification tools."""
    print("CNS Local Hub - macOS Notification Tools Check")
    print("=" * 50)
    
    # Check homebrew
    if not CNSNotificationHandler._check_command_exists(None, 'brew'):
        print("❌ Homebrew not found. Install from: https://brew.sh")
        return False
    
    tools_status = {
        'terminal-notifier': 'brew install terminal-notifier',
        'alerter': 'brew install alerter'
    }
    
    all_good = True
    for tool, install_cmd in tools_status.items():
        if CNSNotificationHandler._check_command_exists(None, tool):
            print(f"✅ {tool} - Available")
        else:
            print(f"❌ {tool} - Missing. Install with: {install_cmd}")
            all_good = False
    
    if all_good:
        print("\n✅ All notification tools ready!")
    else:
        print(f"\n⚠️  Install missing tools, then run: python3 {__file__}")
    
    return all_good


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--check-tools':
        install_macos_tools()
        sys.exit(0)
    
    # Check if we're on macOS
    try:
        subprocess.run(['sw_vers'], check=True, stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        logger.error("This script is designed for macOS. Current system not supported.")
        sys.exit(1)
    
    # Check tools availability but proceed anyway (we have fallbacks)
    tools_available = install_macos_tools()
    if not tools_available:
        logger.warning("Some notification tools missing, but proceeding with available fallbacks")
    
    start_hub_server()