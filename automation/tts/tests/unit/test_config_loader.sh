#!/bin/bash

# Unit tests for config_loader.sh module

# Source the module under test
source "$(dirname "${BASH_SOURCE[0]}")/../../lib/common/config_loader.sh"

# Test configuration loading
test_load_tts_config() {
    start_test "load_tts_config with valid config"
    
    # Create test config
    local test_config=$(create_temp_file '{
        "speech": {"rate_wpm": 180, "volume": 0.8},
        "timing": {"max_full_response_seconds": 15},
        "paths": {"debug_log": "/tmp/test.log"}
    }' ".json")
    
    # Test loading
    if load_tts_config "$test_config"; then
        # Verify values were loaded
        local rate=$(get_config_value "speech.rate_wpm")
        assert_equals "180" "$rate" "Speech rate should be loaded correctly"
    else
        fail_test "Failed to load valid config"
    fi
}

test_load_invalid_json() {
    start_test "load_tts_config with invalid JSON"
    
    # Create invalid JSON
    local test_config=$(create_temp_file '{"invalid": json}' ".json")
    
    # Should fail
    assert_failure "load_tts_config '$test_config'" "Should fail with invalid JSON"
}

test_get_config_value() {
    start_test "get_config_value with existing key"
    
    # Set up test data
    TTS_CONFIG["test.key"]="test_value"
    
    local value=$(get_config_value "test.key")
    assert_equals "test_value" "$value" "Should return correct config value"
}

test_get_config_value_with_default() {
    start_test "get_config_value with default for missing key"
    
    local value=$(get_config_value "nonexistent.key" "default_value")
    assert_equals "default_value" "$value" "Should return default value"
}

test_validate_config() {
    start_test "validate_config with valid values"
    
    # Set up valid config values
    TTS_CONFIG["speech.rate_wpm"]="200"
    TTS_CONFIG["timing.max_full_response_seconds"]="10"
    TTS_CONFIG["paths.debug_log"]="/tmp/test.log"
    
    # Ensure debug log directory exists
    mkdir -p "$(dirname "${TTS_CONFIG["paths.debug_log"]}")"
    
    assert_success "validate_config" "Should pass validation with valid config"
}

test_validate_config_invalid_rate() {
    start_test "validate_config with invalid speech rate"
    
    # Set invalid speech rate
    TTS_CONFIG["speech.rate_wpm"]="1000"  # Too high
    TTS_CONFIG["timing.max_full_response_seconds"]="10"
    TTS_CONFIG["paths.debug_log"]="/tmp/test.log"
    
    assert_failure "validate_config" "Should fail validation with invalid speech rate"
}

test_calculate_derived_config() {
    start_test "calculate_derived_config"
    
    # Set up base values
    TTS_CONFIG["speech.chars_per_second"]="16.5"
    TTS_CONFIG["timing.target_min_seconds"]="5"
    TTS_CONFIG["timing.target_max_seconds"]="25"
    
    calculate_derived_config
    
    local min_chars=$(get_config_value "derived.target_min_chars")
    local max_chars=$(get_config_value "derived.target_max_chars")
    
    # 5 * 16.5 = 82.5, rounded to 83
    assert_equals "83" "$min_chars" "Min chars should be calculated correctly"
    
    # 25 * 16.5 = 412.5, rounded to 413
    assert_equals "413" "$max_chars" "Max chars should be calculated correctly"
}

# Run all tests
test_load_tts_config
test_load_invalid_json  
test_get_config_value
test_get_config_value_with_default
test_validate_config
test_validate_config_invalid_rate
test_calculate_derived_config