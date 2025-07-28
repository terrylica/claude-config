#!/usr/bin/env python3
"""
Claude Code Auto-Follow-up Trigger Hook

This script analyzes Claude Code sessions to detect completion of long action sequences
and automatically trigger follow-up prompts when appropriate.

Usage: Called automatically by Claude Code Stop hook
Input: JSON session data via stdin
Output: JSON control commands to stdout
"""

import json
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

# Import emergency controls
try:
    from pathlib import Path
    emergency_controls_path = Path(__file__).parent / "emergency-controls.py"
    if emergency_controls_path.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("emergency_controls", emergency_controls_path)
        emergency_controls = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(emergency_controls)
        EmergencyControls = emergency_controls.EmergencyControls
    else:
        EmergencyControls = None
except Exception:
    EmergencyControls = None

# Configuration
MAX_FOLLOWUP_DEPTH = 3
STATE_FILE = Path.home() / ".claude" / "hooks" / "session-state.json"
LOG_FILE = Path.home() / ".claude" / "hooks" / "followup.log"
LONG_SEQUENCE_THRESHOLD = 5  # Minimum number of tool uses to consider "long"
FOLLOWUP_COOLDOWN_MINUTES = 2  # Minimum time between follow-ups

class FollowupTrigger:
    def __init__(self):
        self.session_data = None
        self.state = self._load_state()
        self.emergency_controls = EmergencyControls() if EmergencyControls else None
        
    def _load_state(self) -> Dict:
        """Load persistent session state"""
        try:
            if STATE_FILE.exists():
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self._log(f"Error loading state: {e}")
        return {"sessions": {}, "last_followup": None}
    
    def _save_state(self):
        """Save persistent session state"""
        try:
            STATE_FILE.parent.mkdir(exist_ok=True)
            with open(STATE_FILE, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            self._log(f"Error saving state: {e}")
    
    def _log(self, message: str):
        """Log to debug file"""
        try:
            LOG_FILE.parent.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(LOG_FILE, 'a') as f:
                f.write(f"[{timestamp}] {message}\n")
        except Exception:
            pass  # Silent failure for logging
    
    def _get_session_id(self) -> Optional[str]:
        """Extract session ID from stdin data"""
        if not self.session_data:
            return None
        
        # Try to extract session identifier from various possible fields
        possible_fields = ['session_id', 'id', 'conversation_id', 'thread_id']
        for field in possible_fields:
            if field in self.session_data:
                return str(self.session_data[field])
        
        # Fallback: use timestamp-based identifier
        return f"session_{int(time.time())}"
    
    def _analyze_action_sequence(self) -> Dict[str, Any]:
        """Analyze the session to detect action patterns"""
        analysis = {
            "tool_count": 0,
            "file_operations": 0,
            "edit_operations": 0,
            "bash_commands": 0,
            "git_operations": 0,
            "has_errors": False,
            "action_types": set(),
            "files_modified": set(),
            "last_action_time": None
        }
        
        if not self.session_data:
            return analysis
        
        # Extract tool usage patterns from session data
        # Note: The exact structure depends on what Claude Code provides
        # This is a general approach that can be refined based on actual data
        
        # Look for evidence of tool usage in various possible locations
        tools_used = []
        
        # Check common fields where tool information might be stored
        if 'tools' in self.session_data:
            tools_used.extend(self.session_data['tools'])
        elif 'actions' in self.session_data:
            tools_used.extend(self.session_data['actions'])
        elif 'history' in self.session_data:
            tools_used.extend(self.session_data['history'])
        
        # Analyze tool usage patterns
        for tool in tools_used:
            tool_name = tool.get('name', '').lower() if isinstance(tool, dict) else str(tool).lower()
            analysis["action_types"].add(tool_name)
            
            if tool_name in ['edit', 'multiedit', 'write']:
                analysis["edit_operations"] += 1
                analysis["file_operations"] += 1
                
                # Track modified files
                if isinstance(tool, dict) and 'file_path' in tool:
                    analysis["files_modified"].add(tool['file_path'])
                    
            elif tool_name in ['bash', 'shell', 'command']:
                analysis["bash_commands"] += 1
                
                # Check for git operations
                if isinstance(tool, dict) and 'command' in tool:
                    cmd = tool['command'].lower()
                    if any(git_cmd in cmd for git_cmd in ['git add', 'git commit', 'git push', 'git status']):
                        analysis["git_operations"] += 1
                        
            elif tool_name in ['read', 'glob', 'grep']:
                analysis["file_operations"] += 1
            
            # Check for errors
            if isinstance(tool, dict) and ('error' in tool or 'failed' in str(tool).lower()):
                analysis["has_errors"] = True
        
        analysis["tool_count"] = len(tools_used)
        analysis["action_types"] = list(analysis["action_types"])  # Convert set to list for JSON
        analysis["files_modified"] = list(analysis["files_modified"])
        
        return analysis
    
    def _should_trigger_followup(self, session_id: str, analysis: Dict[str, Any]) -> tuple[bool, str]:
        """Determine if a follow-up prompt should be triggered"""
        
        # Emergency controls safety checks
        if self.emergency_controls:
            # Check if emergency stop is active
            if self.emergency_controls.is_emergency_stop_active():
                return False, "Emergency stop is active"
            
            # Check usage limits
            within_limits, limit_msg = self.emergency_controls.check_usage_limits()
            if not within_limits:
                return False, f"Usage limits exceeded: {limit_msg}"
        
        # Check cooldown period
        last_followup = self.state.get("last_followup")
        if last_followup:
            last_time = datetime.fromisoformat(last_followup)
            if datetime.now() - last_time < timedelta(minutes=FOLLOWUP_COOLDOWN_MINUTES):
                return False, "Cooldown period active"
        
        # Check follow-up depth to prevent loops
        session_info = self.state["sessions"].get(session_id, {"followup_count": 0})
        if session_info["followup_count"] >= MAX_FOLLOWUP_DEPTH:
            return False, "Maximum follow-up depth reached"
        
        # Analyze if this qualifies as a "long action sequence"
        if analysis["tool_count"] < LONG_SEQUENCE_THRESHOLD:
            return False, f"Tool count {analysis['tool_count']} below threshold {LONG_SEQUENCE_THRESHOLD}"
        
        # Specific triggers for follow-ups
        triggers = []
        
        # Code changes without commits
        if analysis["file_operations"] > 0 and analysis["git_operations"] == 0:
            triggers.append("APCF")  # Auto-commit with SR&ED evidence
        
        # Multiple file edits without testing
        if analysis["edit_operations"] >= 3 and analysis["bash_commands"] == 0:
            triggers.append("run_tests")
        
        # Error-prone operations
        if analysis["has_errors"]:
            triggers.append("error_review")
        
        # Complex operations (many tools used)
        if analysis["tool_count"] >= 10:
            triggers.append("complexity_review")
        
        if not triggers:
            return False, "No follow-up triggers detected"
        
        return True, f"Triggers: {', '.join(triggers)}"
    
    def _get_followup_prompt(self, analysis: Dict[str, Any], trigger_reason: str) -> str:
        """Generate appropriate follow-up prompt based on analysis"""
        
        # Priority order: errors first, then complexity, then testing, then APCF
        # Error review follow-up (highest priority)
        if "error_review" in trigger_reason:
            return "Please review the errors that occurred and suggest improvements or fixes."
        
        # Complexity review for large operations
        if "complexity_review" in trigger_reason:
            return "Please review the changes made and suggest any optimizations or documentation updates needed."
        
        # Testing follow-up for extensive code changes
        if "run_tests" in trigger_reason:
            return "Please run the appropriate tests for the changes made and fix any issues that arise."
        
        # APCF (Audit-Proof Commit Format) is the most common follow-up
        if "APCF" in trigger_reason:
            return "APCF"
        
        # Default follow-up
        return "Please review the completed work and suggest any next steps or improvements."
    
    def run(self) -> Dict[str, Any]:
        """Main execution logic"""
        try:
            # Read session data from stdin
            stdin_data = sys.stdin.read().strip()
            if stdin_data:
                self.session_data = json.loads(stdin_data)
            
            self._log(f"Processing session data: {json.dumps(self.session_data, indent=2) if self.session_data else 'No data'}")
            
            session_id = self._get_session_id()
            if not session_id:
                self._log("No session ID found, skipping follow-up")
                return {"continue": True}
            
            # Analyze the action sequence
            analysis = self._analyze_action_sequence()
            self._log(f"Analysis for session {session_id}: {json.dumps(analysis, indent=2)}")
            
            # Check if follow-up should be triggered
            should_trigger, reason = self._should_trigger_followup(session_id, analysis)
            self._log(f"Follow-up decision: {should_trigger}, reason: {reason}")
            
            if not should_trigger:
                return {"continue": True}
            
            # Generate follow-up prompt
            followup_prompt = self._get_followup_prompt(analysis, reason)
            
            # Update session state
            self.state["sessions"][session_id] = {
                "followup_count": self.state["sessions"].get(session_id, {}).get("followup_count", 0) + 1,
                "last_analysis": analysis,
                "last_followup": datetime.now().isoformat()
            }
            self.state["last_followup"] = datetime.now().isoformat()
            self._save_state()
            
            # Record usage for safety tracking
            if self.emergency_controls:
                self.emergency_controls.record_usage()
            
            self._log(f"Triggering follow-up: {followup_prompt}")
            
            # Return control command to block stopping and provide follow-up prompt
            return {
                "decision": "block",
                "reason": followup_prompt,
                "continue": False
            }
            
        except Exception as e:
            self._log(f"Error in followup trigger: {e}")
            import traceback
            self._log(f"Traceback: {traceback.format_exc()}")
            return {"continue": True}

def main():
    """Entry point for the hook"""
    trigger = FollowupTrigger()
    result = trigger.run()
    
    # Output result as JSON
    print(json.dumps(result))

if __name__ == "__main__":
    main()