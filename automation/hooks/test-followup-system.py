#!/usr/bin/env python3
"""
Test Script for Claude Code Auto-Follow-up System

This script tests the followup-trigger.py system with various simulated scenarios.
"""

import json
import sys
import subprocess
from pathlib import Path
from typing import Dict, Any

def create_test_session_data(scenario: str) -> Dict[str, Any]:
    """Create test session data for different scenarios"""
    
    base_data = {
        "session_id": f"test_session_{scenario}",
        "timestamp": "2025-07-24T10:00:00",
        "tools": []
    }
    
    if scenario == "short_sequence":
        # Short sequence - should not trigger follow-up
        base_data["tools"] = [
            {"name": "read", "file_path": "test.py"},
            {"name": "edit", "file_path": "test.py", "success": True}
        ]
    
    elif scenario == "long_sequence_no_commit":
        # Long sequence without commit - should trigger APCF
        base_data["tools"] = [
            {"name": "read", "file_path": "main.py"},
            {"name": "edit", "file_path": "main.py", "success": True},
            {"name": "write", "file_path": "utils.py", "success": True},
            {"name": "edit", "file_path": "config.py", "success": True},
            {"name": "read", "file_path": "README.md"},
            {"name": "multiedit", "file_path": "tests.py", "success": True}
        ]
    
    elif scenario == "long_sequence_with_errors":
        # Long sequence with errors - should trigger error review
        base_data["tools"] = [
            {"name": "bash", "command": "python test.py", "error": "SyntaxError"},
            {"name": "edit", "file_path": "test.py", "success": True},
            {"name": "bash", "command": "python test.py", "error": "ImportError"},
            {"name": "edit", "file_path": "requirements.txt", "success": True},
            {"name": "bash", "command": "pip install -r requirements.txt", "success": True},
            {"name": "bash", "command": "python test.py", "success": True}
        ]
    
    elif scenario == "complex_sequence":
        # Very complex sequence - should trigger complexity review
        tools = []
        for i in range(15):
            tools.append({"name": "edit", "file_path": f"file_{i}.py", "success": True})
        base_data["tools"] = tools
    
    elif scenario == "sequence_with_tests":
        # Sequence with bash commands (testing) - should not trigger run_tests
        base_data["tools"] = [
            {"name": "edit", "file_path": "main.py", "success": True},
            {"name": "edit", "file_path": "test_main.py", "success": True},
            {"name": "bash", "command": "pytest", "success": True},
            {"name": "edit", "file_path": "utils.py", "success": True},
            {"name": "bash", "command": "python -m pytest", "success": True}
        ]
    
    return base_data

def run_test(scenario: str, expected_result: str) -> tuple[bool, str, Dict]:
    """Run a single test scenario"""
    print(f"\n🧪 Testing scenario: {scenario}")
    print(f"   Expected: {expected_result}")
    
    # Clear state files before each test to avoid cooldown interference
    state_file = Path.home() / ".claude" / "hooks" / "session-state.json"
    if state_file.exists():
        state_file.unlink()
    
    # Create test data with unique session ID
    test_data = create_test_session_data(scenario)
    test_json = json.dumps(test_data)
    
    # Run the followup trigger script
    try:
        script_path = Path.home() / ".claude" / "hooks" / "followup-trigger.py"
        result = subprocess.run(
            [sys.executable, str(script_path)],
            input=test_json,
            text=True,
            capture_output=True,
            timeout=10
        )
        
        if result.returncode != 0:
            return False, f"Script failed with return code {result.returncode}: {result.stderr}", {}
        
        # Parse the output
        try:
            output_data = json.loads(result.stdout.strip())
        except json.JSONDecodeError:
            return False, f"Invalid JSON output: {result.stdout}", {}
        
        # Check if follow-up was triggered
        followup_triggered = output_data.get("decision") == "block"
        followup_reason = output_data.get("reason", "")
        
        print(f"   Result: {'✅ Follow-up triggered' if followup_triggered else '⏭️  No follow-up'}")
        if followup_triggered:
            print(f"   Follow-up: {followup_reason}")
        
        # Determine if test passed
        if expected_result == "followup" and followup_triggered:
            return True, "PASS - Follow-up triggered as expected", output_data
        elif expected_result == "no_followup" and not followup_triggered:
            return True, "PASS - No follow-up as expected", output_data
        elif expected_result == "APCF" and followup_triggered and "APCF" in followup_reason:
            return True, "PASS - APCF follow-up triggered as expected", output_data
        elif expected_result == "error_review" and followup_triggered and "error" in followup_reason.lower():
            return True, "PASS - Error review triggered as expected", output_data
        elif expected_result == "complexity_review" and followup_triggered and "optimization" in followup_reason.lower():
            return True, "PASS - Complexity review triggered as expected", output_data
        elif expected_result == "run_tests" and followup_triggered and "test" in followup_reason.lower():
            return True, "PASS - Run tests triggered as expected", output_data
        else:
            return False, f"FAIL - Expected {expected_result}, got {'followup' if followup_triggered else 'no_followup'}", output_data
            
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT - Script took too long to execute", {}
    except Exception as e:
        return False, f"ERROR - {str(e)}", {}

def test_emergency_controls():
    """Test emergency controls functionality"""
    print("\n🛡️  Testing Emergency Controls")
    
    try:
        controls_path = Path.home() / ".claude" / "hooks" / "emergency-controls.py"
        
        # Test status command
        result = subprocess.run(
            [sys.executable, str(controls_path), "status"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            status_data = json.loads(result.stdout)
            print("   ✅ Emergency controls working")
            print(f"   📊 Status: {status_data}")
            return True
        else:
            print(f"   ❌ Emergency controls failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"   ❌ Emergency controls error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Claude Code Auto-Follow-up System Test Suite")
    print("=" * 60)
    
    # Test scenarios
    test_cases = [
        ("short_sequence", "no_followup"),
        ("long_sequence_no_commit", "run_tests"),  # Multiple edits without tests trigger run_tests (higher priority than APCF)
        ("long_sequence_with_errors", "error_review"),
        ("complex_sequence", "complexity_review"),
        ("sequence_with_tests", "APCF")  # This should trigger APCF since there are file edits without commits
    ]
    
    passed = 0
    total = len(test_cases)
    
    # Run followup trigger tests
    for scenario, expected in test_cases:
        success, message, data = run_test(scenario, expected)
        if success:
            passed += 1
        print(f"   {message}")
    
    # Test emergency controls
    if test_emergency_controls():
        passed += 1
        total += 1
    else:
        total += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📋 Test Summary: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
    else:
        print(f"⚠️  {total - passed} tests failed. Please review the issues above.")
    
    # Show log file location
    log_file = Path.home() / ".claude" / "hooks" / "followup.log"
    if log_file.exists():
        print(f"📝 Check logs at: {log_file}")

if __name__ == "__main__":
    main()