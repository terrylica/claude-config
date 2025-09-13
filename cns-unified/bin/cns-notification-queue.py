#!/usr/bin/env python3
"""
CNS Notification Queue Processor
Monitors notification queue and executes visual/audio notifications.
Runs as separate user process (not LaunchAgent) to avoid subprocess restrictions.
"""

import json
import logging
import subprocess
import sys
import time
from pathlib import Path
from threading import Thread
import fcntl

# Configuration
QUEUE_FILE = "/tmp/cns-notification-queue.jsonl"
LOCK_FILE = "/tmp/cns-queue-processor.lock"
LOG_FILE = "/tmp/cns-queue-processor.log"

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


def acquire_lock():
    """Acquire exclusive lock to prevent multiple processors."""
    try:
        lock_fd = open(LOCK_FILE, 'w')
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        lock_fd.write(str(os.getpid()))
        lock_fd.flush()
        return lock_fd
    except (OSError, IOError):
        return None


def trigger_macos_notification(title, message):
    """Trigger macOS notification using available tools."""
    try:
        # Try terminal-notifier first (most reliable)
        try:
            cmd = ['terminal-notifier', '-title', title, '-message', message, 
                   '-sound', 'default']
            subprocess.run(cmd, check=True, timeout=5)
            logger.info(f"Notification sent: {title}")
            return
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Fallback to alerter
        try:
            cmd = ['alerter', '-title', title, '-message', message]
            subprocess.run(cmd, check=True, timeout=5)
            logger.info(f"Notification sent via alerter: {title}")
            return
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Fallback to osascript
        script = f'display notification "{message}" with title "{title}"'
        try:
            cmd = ['osascript', '-e', script]
            subprocess.run(cmd, check=True, timeout=5)
            logger.info(f"Notification sent via osascript: {title}")
            return
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass
            
        logger.warning(f"All notification methods failed for: {title} - {message}")
        
    except Exception as e:
        logger.error(f"Notification error: {e}")


def trigger_audio_notification(text):
    """Trigger audio notification using TTS."""
    try:
        # Play toy-story notification sound
        sound_file = "/Users/terryli/.claude/media/toy-story-notification.mp3"
        if Path(sound_file).exists():
            try:
                subprocess.run([
                    'afplay', sound_file
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
                logger.info("Played notification sound")
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                logger.warning("Failed to play notification sound")
        
        # Follow with TTS
        if text and len(text.strip()) > 0:
            try:
                subprocess.Popen([
                    'say', text
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                logger.info(f"Triggered TTS for: {text[:50]}...")
            except Exception as e:
                logger.error(f"TTS failed: {e}")
    except Exception as e:
        logger.error(f"Audio notification error: {e}")


def copy_to_clipboard(text):
    """Copy text to macOS clipboard."""
    try:
        process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
        process.communicate(input=text.encode('utf-8'))
        logger.info("Content copied to clipboard")
    except Exception as e:
        logger.error(f"Clipboard copy failed: {e}")


def process_notification_queue():
    """Process notifications from the queue file."""
    if not Path(QUEUE_FILE).exists():
        return
    
    try:
        with open(QUEUE_FILE, 'r') as f:
            lines = f.readlines()
        
        if not lines:
            return
        
        # Clear the queue file after reading
        Path(QUEUE_FILE).write_text("")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            try:
                notification = json.loads(line)
                title = notification.get('title', 'CNS Notification')
                message = notification.get('message', '')
                clipboard = notification.get('clipboard', False)
                audio = notification.get('audio', True)
                
                logger.info(f"Processing notification: {title}")
                
                # Trigger notifications
                trigger_macos_notification(title, message)
                
                if clipboard:
                    copy_to_clipboard(message)
                
                if audio and len(message) > 2:
                    trigger_audio_notification(message[:200])
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse notification: {e}")
            except Exception as e:
                logger.error(f"Failed to process notification: {e}")
                
    except Exception as e:
        logger.error(f"Error processing queue: {e}")


def monitor_queue():
    """Monitor queue file for new notifications."""
    logger.info("CNS Notification Queue Processor started")
    
    while True:
        try:
            process_notification_queue()
            time.sleep(1)  # Check every second
        except KeyboardInterrupt:
            logger.info("Queue processor shutting down")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(5)  # Wait longer on errors


if __name__ == '__main__':
    import os
    
    # Acquire lock to prevent multiple instances
    lock_fd = acquire_lock()
    if not lock_fd:
        print("Another queue processor is already running")
        sys.exit(1)
    
    try:
        monitor_queue()
    finally:
        if lock_fd:
            lock_fd.close()
            Path(LOCK_FILE).unlink(missing_ok=True)