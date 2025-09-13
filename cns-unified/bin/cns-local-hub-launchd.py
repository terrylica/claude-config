#!/usr/bin/env python3
"""
CNS Local Hub (LaunchAgent Compatible) - macOS Notification Server
LaunchAgent-compatible version that defers subprocess usage to avoid resource limits.
Part of the CNS remote alert transmission system.
"""

import json
import logging
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import urlparse

# Configuration
HUB_HOST = '127.0.0.1'
HUB_PORT = 5050
LOG_FILE = '/tmp/cns-local-hub-launchd.log'

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


def queue_notification(title, message, clipboard=False, audio=True):
    """Queue notification for processing by separate queue processor."""
    try:
        notification = {
            'title': title,
            'message': message,
            'clipboard': clipboard,
            'audio': audio,
            'timestamp': time.time()
        }
        
        queue_file = "/tmp/cns-notification-queue.jsonl"
        with open(queue_file, 'a') as f:
            f.write(json.dumps(notification) + '\n')
        
        logger.info(f"Queued notification: {title}")
        
    except Exception as e:
        logger.error(f"Failed to queue notification: {e}")


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
                data = json.loads(body)
                title = data.get('title', 'CNS Notification')
                message = data.get('message', body)
            except json.JSONDecodeError:
                title = 'CNS Remote Alert'
                message = body
            
            logger.info(f"Received notification: {title} - {message[:100]}...")
            
            # Queue notification for processing by separate queue processor
            clipboard = hasattr(self, 'CLAUDE_CNS_CLIPBOARD') or 'CLAUDE_CNS_CLIPBOARD' in body
            audio = len(message) > 2  # Allow short directory names
            
            queue_notification(title, message, clipboard=clipboard, audio=audio)
            
            # Send success response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "success", "message": "Notification processed"}')
            
        except Exception as e:
            logger.error(f"Error processing notification: {e}")
            self.send_error(500, f"Internal error: {str(e)}")
    
    def do_GET(self):
        """Handle GET requests (health check)."""
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'healthy')
        else:
            self.send_error(404, "Not found")
    
    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.info(f"{self.address_string()} - {format % args}")


def start_hub_server():
    """Start the CNS hub server."""
    try:
        server = HTTPServer((HUB_HOST, HUB_PORT), CNSNotificationHandler)
        logger.info(f"CNS Hub LaunchAgent starting on {HUB_HOST}:{HUB_PORT}")
        
        # Start server in background thread for graceful shutdown handling
        def serve_forever():
            server.serve_forever()
        
        server_thread = Thread(target=serve_forever, daemon=True)
        server_thread.start()
        
        logger.info(f"CNS Hub LaunchAgent running on {HUB_HOST}:{HUB_PORT}")
        
        # Keep main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("CNS Hub LaunchAgent shutting down...")
            server.shutdown()
            server.server_close()
            
    except OSError as e:
        if e.errno == 48:  # Address already in use
            logger.error(f"Port {HUB_PORT} already in use. Is another hub running?")
        else:
            logger.error(f"Failed to start server: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    # Skip all subprocess-based initialization checks for LaunchAgent compatibility
    logger.info("CNS Hub LaunchAgent - skipping initialization subprocess calls")
    start_hub_server()