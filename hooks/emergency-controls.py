#!/usr/bin/env python3
"""
Emergency Controls for Claude Code Auto-Follow-up System

This script provides emergency controls and safety mechanisms for the follow-up trigger system.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any

class EmergencyControls:
    def __init__(self):
        self.hooks_dir = Path.home() / ".claude" / "hooks"
        self.safety_config_file = self.hooks_dir / "safety-config.json"
        self.emergency_file = self.hooks_dir / "EMERGENCY_STOP"
        self.usage_log = self.hooks_dir / "usage-log.json"
        self.config = self._load_safety_config()
    
    def _load_safety_config(self) -> Dict[str, Any]:
        """Load safety configuration"""
        try:
            if self.safety_config_file.exists():
                with open(self.safety_config_file, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        
        # Default safety config
        return {
            "safety_settings": {
                "max_followup_depth": 3,
                "followup_cooldown_minutes": 2,
                "emergency_brake": {
                    "enabled": True,
                    "max_daily_followups": 50,
                    "max_hourly_followups": 10
                }
            }
        }
    
    def _load_usage_log(self) -> Dict[str, Any]:
        """Load usage statistics"""
        try:
            if self.usage_log.exists():
                with open(self.usage_log, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        return {"daily_count": 0, "hourly_counts": {}, "last_reset": None}
    
    def _save_usage_log(self, log_data: Dict[str, Any]):
        """Save usage statistics"""
        try:
            with open(self.usage_log, 'w') as f:
                json.dump(log_data, f, indent=2)
        except Exception:
            pass
    
    def is_emergency_stop_active(self) -> bool:
        """Check if emergency stop is active"""
        return self.emergency_file.exists()
    
    def activate_emergency_stop(self, reason: str = "Manual activation"):
        """Activate emergency stop"""
        try:
            with open(self.emergency_file, 'w') as f:
                f.write(f"Emergency stop activated at {datetime.now().isoformat()}\n")
                f.write(f"Reason: {reason}\n")
                f.write("To deactivate, delete this file or run: python emergency-controls.py deactivate\n")
            print(f"✅ Emergency stop activated: {reason}")
        except Exception as e:
            print(f"❌ Failed to activate emergency stop: {e}")
    
    def deactivate_emergency_stop(self):
        """Deactivate emergency stop"""
        try:
            if self.emergency_file.exists():
                self.emergency_file.unlink()
                print("✅ Emergency stop deactivated")
            else:
                print("ℹ️  Emergency stop was not active")
        except Exception as e:
            print(f"❌ Failed to deactivate emergency stop: {e}")
    
    def check_usage_limits(self) -> tuple[bool, str]:
        """Check if usage limits have been exceeded"""
        if not self.config["safety_settings"]["emergency_brake"]["enabled"]:
            return True, "Emergency brake disabled"
        
        usage_log = self._load_usage_log()
        now = datetime.now()
        
        # Reset daily counter if needed
        last_reset = usage_log.get("last_reset")
        if not last_reset or datetime.fromisoformat(last_reset).date() != now.date():
            usage_log["daily_count"] = 0
            usage_log["hourly_counts"] = {}
            usage_log["last_reset"] = now.isoformat()
        
        # Check daily limit
        max_daily = self.config["safety_settings"]["emergency_brake"]["max_daily_followups"]
        if usage_log["daily_count"] >= max_daily:
            return False, f"Daily limit exceeded ({usage_log['daily_count']}/{max_daily})"
        
        # Check hourly limit
        current_hour = now.strftime("%Y-%m-%d-%H")
        hourly_counts = usage_log.get("hourly_counts", {})
        current_hour_count = hourly_counts.get(current_hour, 0)
        max_hourly = self.config["safety_settings"]["emergency_brake"]["max_hourly_followups"]
        
        if current_hour_count >= max_hourly:
            return False, f"Hourly limit exceeded ({current_hour_count}/{max_hourly})"
        
        return True, "Within limits"
    
    def record_usage(self):
        """Record a follow-up usage"""
        usage_log = self._load_usage_log()
        now = datetime.now()
        
        # Increment daily counter
        usage_log["daily_count"] = usage_log.get("daily_count", 0) + 1
        
        # Increment hourly counter
        current_hour = now.strftime("%Y-%m-%d-%H")
        if "hourly_counts" not in usage_log:
            usage_log["hourly_counts"] = {}
        usage_log["hourly_counts"][current_hour] = usage_log["hourly_counts"].get(current_hour, 0) + 1
        
        # Clean old hourly data (keep only last 24 hours)
        cutoff_time = now - timedelta(hours=24)
        usage_log["hourly_counts"] = {
            hour: count for hour, count in usage_log["hourly_counts"].items()
            if datetime.strptime(hour, "%Y-%m-%d-%H") > cutoff_time
        }
        
        self._save_usage_log(usage_log)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        usage_log = self._load_usage_log()
        within_limits, limit_msg = self.check_usage_limits()
        
        return {
            "emergency_stop_active": self.is_emergency_stop_active(),
            "within_usage_limits": within_limits,
            "usage_limit_message": limit_msg,
            "daily_usage": usage_log.get("daily_count", 0),
            "max_daily": self.config["safety_settings"]["emergency_brake"]["max_daily_followups"],
            "safety_config_loaded": bool(self.config)
        }

def main():
    """Command-line interface for emergency controls"""
    controls = EmergencyControls()
    
    if len(sys.argv) < 2:
        # Show status
        status = controls.get_status()
        print("🔧 Claude Code Follow-up System Status:")
        print(f"   Emergency Stop: {'🔴 ACTIVE' if status['emergency_stop_active'] else '🟢 Inactive'}")
        print(f"   Usage Limits: {'🟢 OK' if status['within_usage_limits'] else '🔴 EXCEEDED'}")
        print(f"   Daily Usage: {status['daily_usage']}/{status['max_daily']}")
        print(f"   Limit Status: {status['usage_limit_message']}")
        print("\nCommands:")
        print("   python emergency-controls.py activate [reason]  - Activate emergency stop")
        print("   python emergency-controls.py deactivate        - Deactivate emergency stop")
        print("   python emergency-controls.py status            - Show detailed status")
        return
    
    command = sys.argv[1].lower()
    
    if command == "activate":
        reason = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "Manual activation"
        controls.activate_emergency_stop(reason)
    elif command == "deactivate":
        controls.deactivate_emergency_stop()
    elif command == "status":
        status = controls.get_status()
        print(json.dumps(status, indent=2))
    else:
        print(f"❌ Unknown command: {command}")
        print("Available commands: activate, deactivate, status")

if __name__ == "__main__":
    main()