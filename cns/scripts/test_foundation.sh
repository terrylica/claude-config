#!/bin/bash

# Test Foundation Infrastructure
# Quick validation script for the modular TTS foundation

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TTS_DIR="$(dirname "$SCRIPT_DIR")"

echo "=== TTS Foundation Infrastructure Test ==="
echo "TTS Directory: $TTS_DIR"

# Test 1: Configuration Loading
echo
echo "1. Testing Configuration Loading..."
source "$TTS_DIR/lib/common/config_loader.sh"

if init_config; then
    echo "✓ Configuration loaded successfully"
    
    # Test getting values
    speech_rate=$(get_config_value "speech.rate_wpm")
    echo "  - Speech rate: ${speech_rate} WPM"
    
    debug_log=$(get_config_value "paths.debug_log")
    echo "  - Debug log: $debug_log"
    
    # Test derived calculations
    calculate_derived_config
    min_chars=$(get_config_value "derived.target_min_chars")
    max_chars=$(get_config_value "derived.target_max_chars")
    echo "  - Character range: $min_chars - $max_chars chars"
else
    echo "✗ Configuration loading failed"
    exit 1
fi

# Test 2: Logging System
echo
echo "2. Testing Logging System..."
source "$TTS_DIR/lib/common/logger.sh"

init_logging
log_info "TEST" "Foundation infrastructure test started"
log_debug "TEST" "Debug logging is working"
log_warn "TEST" "Warning logging is working"

if [[ -f "$(get_config_value "paths.debug_log")" ]]; then
    echo "✓ Logging system working"
    echo "  - Log file created at: $(get_config_value "paths.debug_log")"
    
    # Show recent log entries
    echo "  - Recent log entries:"
    tail -3 "$(get_config_value "paths.debug_log")" | sed 's/^/    /'
else
    echo "✗ Logging system failed"
    exit 1
fi

# Test 3: Error Handling
echo
echo "3. Testing Error Handling..."
source "$TTS_DIR/lib/common/error_handler.sh"

set_error_context "TEST" "foundation_validation"

# Test successful validation
if check_file_readable "$TTS_DIR/config/tts_config.json" "TTS config"; then
    echo "✓ Error handling validation passed"
else
    echo "✗ Error handling validation failed"
    exit 1
fi

# Test error description
error_desc=$(get_error_description "$ERR_FILE_NOT_FOUND")
echo "  - Error description test: $error_desc"

# Test 4: Directory Structure
echo
echo "4. Testing Directory Structure..."
expected_dirs=(
    "config"
    "lib/common"
    "lib/input" 
    "lib/processing"
    "lib/output"
    "lib/testing"
    "bin"
    "tests/unit"
    "tests/integration"
    "scripts"
    "docs"
)

missing_dirs=()
for dir in "${expected_dirs[@]}"; do
    if [[ ! -d "$TTS_DIR/$dir" ]]; then
        missing_dirs+=("$dir")
    fi
done

if [[ ${#missing_dirs[@]} -eq 0 ]]; then
    echo "✓ All expected directories present"
    echo "  - Total directories: ${#expected_dirs[@]}"
else
    echo "✗ Missing directories: ${missing_dirs[*]}"
    exit 1
fi

# Test 5: Configuration Files
echo
echo "5. Testing Configuration Files..."
config_files=(
    "config/tts_config.json"
    "config/speech_profiles.json"
    "config/text_processing_rules.json"
    "config/debug_config.json"
)

missing_configs=()
for config in "${config_files[@]}"; do
    if [[ ! -f "$TTS_DIR/$config" ]]; then
        missing_configs+=("$config")
    elif ! jq empty "$TTS_DIR/$config" 2>/dev/null; then
        echo "✗ Invalid JSON in: $config"
        exit 1
    fi
done

if [[ ${#missing_configs[@]} -eq 0 ]]; then
    echo "✓ All configuration files present and valid"
    echo "  - Total config files: ${#config_files[@]}"
else
    echo "✗ Missing/invalid config files: ${missing_configs[*]}"
    exit 1
fi

# Test 6: Module Loading
echo
echo "6. Testing Module Loading..."
modules=(
    "lib/common/config_loader.sh"
    "lib/common/logger.sh"
    "lib/common/error_handler.sh"
    "lib/testing/test_runner.sh"
)

for module in "${modules[@]}"; do
    if [[ -f "$TTS_DIR/$module" ]] && bash -n "$TTS_DIR/$module"; then
        echo "  ✓ $module - syntax OK"
    else
        echo "  ✗ $module - syntax error or missing"
        exit 1
    fi
done

echo "✓ All modules have valid syntax"

# Summary
echo
echo "=== Foundation Infrastructure Test Results ==="
echo "✓ Configuration system: WORKING"
echo "✓ Logging system: WORKING"  
echo "✓ Error handling: WORKING"
echo "✓ Directory structure: COMPLETE"
echo "✓ Configuration files: VALID"
echo "✓ Module loading: SUCCESS"
echo
echo "🎉 Foundation infrastructure is ready for Phase 2!"
echo
echo "Next steps:"
echo "1. Extract input processing modules (JSON parser, transcript monitor)"
echo "2. Extract text processing pipeline (sanitizer, aggregator)"
echo "3. Extract output systems (speech synthesizer, debug exporter)"
echo "4. Create main orchestrator"

log_info "TEST" "Foundation infrastructure test completed successfully"