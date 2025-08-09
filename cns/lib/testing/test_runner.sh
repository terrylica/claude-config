#!/bin/bash

# Test Runner Module
# Provides basic unit testing framework for TTS modules

# Test statistics
declare -g TESTS_RUN=0
declare -g TESTS_PASSED=0
declare -g TESTS_FAILED=0
declare -g CURRENT_TEST=""

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

# Initialize test environment
init_test_environment() {
    TESTS_RUN=0
    TESTS_PASSED=0
    TESTS_FAILED=0
    
    echo "Initializing test environment..."
    
    # Create temporary test directory
    export TEST_TEMP_DIR="/tmp/tts_test_$$"
    mkdir -p "$TEST_TEMP_DIR"
    
    # Set up test configuration
    export TEST_CONFIG_DIR="$TEST_TEMP_DIR/config"
    mkdir -p "$TEST_CONFIG_DIR"
    
    # Create minimal test configuration
    cat > "$TEST_CONFIG_DIR/tts_config.json" << 'EOF'
{
  "speech": {"rate_wpm": 200, "chars_per_second": 16.67},
  "timing": {"max_full_response_seconds": 10, "target_min_seconds": 5},
  "paths": {"debug_log": "/tmp/test_debug.log"},
  "features": {"enable_clipboard_debug": false}
}
EOF
}

# Cleanup test environment
cleanup_test_environment() {
    if [[ -n "$TEST_TEMP_DIR" && -d "$TEST_TEMP_DIR" ]]; then
        rm -rf "$TEST_TEMP_DIR"
    fi
}

# Start a test case
start_test() {
    local test_name="$1"
    CURRENT_TEST="$test_name"
    echo -n "Testing: $test_name ... "
}

# Assert that a condition is true
assert_true() {
    local condition="$1"
    local message="${2:-Assertion failed}"
    
    if eval "$condition"; then
        pass_test
    else
        fail_test "$message"
    fi
}

# Assert that two values are equal
assert_equals() {
    local expected="$1"
    local actual="$2"
    local message="${3:-Values not equal}"
    
    if [[ "$expected" == "$actual" ]]; then
        pass_test
    else
        fail_test "$message: expected '$expected', got '$actual'"
    fi
}

# Assert that a command succeeds (exit code 0)
assert_success() {
    local command="$1"
    local message="${2:-Command failed}"
    
    if eval "$command" >/dev/null 2>&1; then
        pass_test
    else
        fail_test "$message: $command"
    fi
}

# Assert that a command fails (non-zero exit code)
assert_failure() {
    local command="$1"
    local message="${2:-Command unexpectedly succeeded}"
    
    if ! eval "$command" >/dev/null 2>&1; then
        pass_test
    else
        fail_test "$message: $command"
    fi
}

# Assert that a file exists
assert_file_exists() {
    local file_path="$1"
    local message="${2:-File does not exist}"
    
    if [[ -f "$file_path" ]]; then
        pass_test
    else
        fail_test "$message: $file_path"
    fi
}

# Assert that a string contains a substring
assert_contains() {
    local haystack="$1"
    local needle="$2"
    local message="${3:-String does not contain expected substring}"
    
    if [[ "$haystack" == *"$needle"* ]]; then
        pass_test
    else
        fail_test "$message: '$haystack' does not contain '$needle'"
    fi
}

# Mark current test as passed
pass_test() {
    ((TESTS_RUN++))
    ((TESTS_PASSED++))
    echo -e "${GREEN}PASS${NC}"
}

# Mark current test as failed
fail_test() {
    local message="$1"
    ((TESTS_RUN++))
    ((TESTS_FAILED++))
    echo -e "${RED}FAIL${NC}"
    if [[ -n "$message" ]]; then
        echo "  ERROR: $message"
    fi
}

# Skip current test
skip_test() {
    local reason="$1"
    echo -e "${YELLOW}SKIP${NC}"
    if [[ -n "$reason" ]]; then
        echo "  REASON: $reason"
    fi
}

# Run a test suite
run_test_suite() {
    local test_file="$1"
    local suite_name="${2:-$(basename "$test_file" .sh)}"
    
    echo "=== Running test suite: $suite_name ==="
    
    if [[ ! -f "$test_file" ]]; then
        echo "ERROR: Test file not found: $test_file"
        return 1
    fi
    
    # Source the test file in a subshell to avoid pollution
    (
        init_test_environment
        source "$test_file"
        cleanup_test_environment
    )
    
    local suite_result=$?
    echo "=== Test suite completed: $suite_name ==="
    return $suite_result
}

# Mock function - replace a command with custom behavior
mock_command() {
    local command_name="$1"
    local mock_behavior="$2"
    
    # Create a mock function
    eval "${command_name}() { $mock_behavior; }"
    export -f "$command_name"
}

# Restore original command
restore_command() {
    local command_name="$1"
    unset -f "$command_name"
}

# Create a temporary file with content
create_temp_file() {
    local content="$1"
    local suffix="${2:-.tmp}"
    
    local temp_file="$TEST_TEMP_DIR/temp_file_$(date +%s)$suffix"
    echo "$content" > "$temp_file"
    echo "$temp_file"
}

# Print test summary
print_test_summary() {
    echo
    echo "=== TEST SUMMARY ==="
    echo "Tests run: $TESTS_RUN"
    echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
    echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
    
    if [[ $TESTS_FAILED -eq 0 ]]; then
        echo -e "${GREEN}All tests passed!${NC}"
        return 0
    else
        echo -e "${RED}Some tests failed!${NC}"
        return 1
    fi
}

# Main test runner function
run_all_tests() {
    local test_dir="${1:-$(dirname "${BASH_SOURCE[0]}")/../tests/unit}"
    
    init_test_environment
    
    echo "Running all tests in: $test_dir"
    
    for test_file in "$test_dir"/test_*.sh; do
        if [[ -f "$test_file" ]]; then
            run_test_suite "$test_file"
        fi
    done
    
    print_test_summary
    local result=$?
    
    cleanup_test_environment
    return $result
}

# Export functions for use in test files
export -f init_test_environment cleanup_test_environment start_test assert_true assert_equals
export -f assert_success assert_failure assert_file_exists assert_contains pass_test fail_test
export -f skip_test run_test_suite mock_command restore_command create_temp_file print_test_summary