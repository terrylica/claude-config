#!/bin/bash

# Integration tests for foundation infrastructure components

# Source required modules
source "$(dirname "${BASH_SOURCE[0]}")/../../lib/common/config_loader.sh"
source "$(dirname "${BASH_SOURCE[0]}")/../../lib/common/logger.sh"
source "$(dirname "${BASH_SOURCE[0]}")/../../lib/common/error_handler.sh"

test_config_and_logging_integration() {
    start_test "Configuration and logging integration"
    
    # Initialize configuration
    if init_config; then
        # Initialize logging (should use config values)
        init_logging
        
        # Test logging with different levels
        log_info "TEST" "Integration test message"
        log_debug "TEST" "Debug message for integration test"
        
        # Verify log file was created
        local log_file=$(get_config_value "paths.debug_log")
        assert_file_exists "$log_file" "Log file should be created"
        
        # Verify log content
        if [[ -f "$log_file" ]]; then
            local log_content=$(tail -1 "$log_file")
            assert_contains "$log_content" "Integration test message" "Log should contain test message"
        fi
        
        pass_test
    else
        fail_test "Failed to initialize configuration"
    fi
}

test_error_handling_with_logging() {
    start_test "Error handling with logging integration"
    
    # Set error context
    set_error_context "TEST_MODULE" "test_operation" "integration_test"
    
    # Handle a test error (without exiting)
    local error_result
    handle_error "$ERR_INVALID_INPUT" "Test error message" false
    error_result=$?
    
    assert_equals "$ERR_INVALID_INPUT" "$error_result" "Should return correct error code"
    
    # Verify error was logged
    local log_file=$(get_config_value "paths.debug_log")
    if [[ -f "$log_file" ]]; then
        local log_content=$(tail -5 "$log_file")
        assert_contains "$log_content" "Test error message" "Error should be logged"
        assert_contains "$log_content" "TEST_MODULE" "Module name should be in log"
    fi
}

test_config_validation_with_error_handling() {
    start_test "Configuration validation with error handling"
    
    # Test with invalid configuration
    TTS_CONFIG["speech.rate_wpm"]="invalid"
    
    # Should handle validation error gracefully
    set_error_context "CONFIG" "validation_test"
    
    if ! validate_config; then
        # This is expected - validation should fail
        log_info "TEST" "Validation correctly failed with invalid config"
        pass_test
    else
        fail_test "Validation should have failed with invalid config"
    fi
}

# Run all integration tests
test_config_and_logging_integration
test_error_handling_with_logging
test_config_validation_with_error_handling