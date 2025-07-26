#!/bin/bash

# Configuration Loader Module
# Handles loading, validation, and access to JSON configuration files

# Configuration file paths (check if already set to avoid readonly errors)
if [[ -z "$TTS_CONFIG_DIR" ]]; then
    readonly TTS_CONFIG_DIR="/Users/terryli/.claude/automation/tts/config"
    readonly TTS_CONFIG_FILE="$TTS_CONFIG_DIR/tts_config.json"
    readonly SPEECH_PROFILES_FILE="$TTS_CONFIG_DIR/speech_profiles.json"
    readonly TEXT_RULES_FILE="$TTS_CONFIG_DIR/text_processing_rules.json"
    readonly DEBUG_CONFIG_FILE="$TTS_CONFIG_DIR/debug_config.json"
fi

# Global configuration variables (using bash 3.x compatible approach)
# Note: Using indexed arrays with naming convention for key-value pairs

# Load and validate main TTS configuration
load_tts_config() {
    local config_file="${1:-$TTS_CONFIG_FILE}"
    
    if [[ ! -f "$config_file" ]]; then
        echo "ERROR: TTS config file not found: $config_file" >&2
        return 1
    fi
    
    if ! jq empty "$config_file" 2>/dev/null; then
        echo "ERROR: Invalid JSON in TTS config file: $config_file" >&2
        return 2
    fi
    
    # Load core configuration values into global variables
    export TTS_SPEECH_RATE_WPM=$(jq -r '.speech.rate_wpm // 198' "$config_file")
    export TTS_SPEECH_CHARS_PER_SECOND=$(jq -r '.speech.chars_per_second // 16.50' "$config_file")
    export TTS_SPEECH_VOICE=$(jq -r '.speech.voice // "default"' "$config_file")
    export TTS_SPEECH_VOLUME=$(jq -r '.speech.volume // 0.7' "$config_file")
    
    export TTS_TIMING_MAX_FULL_RESPONSE_SECONDS=$(jq -r '.timing.max_full_response_seconds // 10' "$config_file")
    export TTS_TIMING_TARGET_MIN_SECONDS=$(jq -r '.timing.target_min_seconds // 5' "$config_file")
    export TTS_TIMING_TARGET_MAX_SECONDS=$(jq -r '.timing.target_max_seconds // 25' "$config_file")
    export TTS_TIMING_MIN_PARAGRAPH_CHARS=$(jq -r '.timing.min_paragraph_chars // 50' "$config_file")
    export TTS_TIMING_POLL_INTERVAL_SECONDS=$(jq -r '.timing.poll_interval_seconds // 0.5' "$config_file")
    export TTS_TIMING_MAX_WAIT_SECONDS=$(jq -r '.timing.max_wait_seconds // 5' "$config_file")
    
    export TTS_PATHS_DEBUG_LOG=$(jq -r '.paths.debug_log // "/tmp/claude_tts_debug.log"' "$config_file")
    export TTS_PATHS_DEBUG_LOG_OLD=$(jq -r '.paths.debug_log_old // "/tmp/claude_tts_debug.log.old"' "$config_file")
    export TTS_PATHS_TEMP_PREFIX=$(jq -r '.paths.temp_prefix // "/tmp/claude_speech_"' "$config_file")
    export TTS_PATHS_CLIPBOARD_PREFIX=$(jq -r '.paths.clipboard_prefix // "/tmp/claude_tts_content_"' "$config_file")
    
    export TTS_FEATURES_ENABLE_CLIPBOARD_DEBUG=$(jq -r '.features.enable_clipboard_debug // true' "$config_file")
    export TTS_FEATURES_ENABLE_GLASS_SOUND=$(jq -r '.features.enable_glass_sound // true' "$config_file")
    export TTS_FEATURES_ENABLE_LOG_ROTATION=$(jq -r '.features.enable_log_rotation // true' "$config_file")
    export TTS_FEATURES_LOG_ROTATION_SIZE_KB=$(jq -r '.features.log_rotation_size_kb // 50' "$config_file")
    
    return 0
}

# Load speech profiles configuration
load_speech_profiles() {
    local config_file="${1:-$SPEECH_PROFILES_FILE}"
    
    if [[ ! -f "$config_file" ]]; then
        echo "WARNING: Speech profiles file not found: $config_file" >&2
        return 1
    fi
    
    if ! jq empty "$config_file" 2>/dev/null; then
        echo "ERROR: Invalid JSON in speech profiles file: $config_file" >&2
        return 2
    fi
    
    # Load default profile settings into global variables
    export TTS_PROFILE_DEFAULT_VOICE=$(jq -r '.profiles.default.voice // "default"' "$config_file")
    export TTS_PROFILE_DEFAULT_RATE_WPM=$(jq -r '.profiles.default.rate_wpm // 198' "$config_file")
    export TTS_PROFILE_DEFAULT_VOLUME=$(jq -r '.profiles.default.volume // 0.7' "$config_file")
    export TTS_PROFILE_DEFAULT_PITCH=$(jq -r '.profiles.default.pitch // 1.0' "$config_file")
    
    return 0
}

# Get configuration value using dot notation
get_config_value() {
    local key="$1"
    local default_value="$2"
    
    if [[ -z "$key" ]]; then
        echo "ERROR: Configuration key is required" >&2
        return 2
    fi
    
    # Convert dot notation to environment variable name
    local var_name
    case "$key" in
        "speech.rate_wpm") var_name="TTS_SPEECH_RATE_WPM" ;;
        "speech.chars_per_second") var_name="TTS_SPEECH_CHARS_PER_SECOND" ;;
        "speech.voice") var_name="TTS_SPEECH_VOICE" ;;
        "speech.volume") var_name="TTS_SPEECH_VOLUME" ;;
        "timing.max_full_response_seconds") var_name="TTS_TIMING_MAX_FULL_RESPONSE_SECONDS" ;;
        "timing.target_min_seconds") var_name="TTS_TIMING_TARGET_MIN_SECONDS" ;;
        "timing.target_max_seconds") var_name="TTS_TIMING_TARGET_MAX_SECONDS" ;;
        "timing.min_paragraph_chars") var_name="TTS_TIMING_MIN_PARAGRAPH_CHARS" ;;
        "timing.poll_interval_seconds") var_name="TTS_TIMING_POLL_INTERVAL_SECONDS" ;;
        "timing.max_wait_seconds") var_name="TTS_TIMING_MAX_WAIT_SECONDS" ;;
        "paths.debug_log") var_name="TTS_PATHS_DEBUG_LOG" ;;
        "paths.debug_log_old") var_name="TTS_PATHS_DEBUG_LOG_OLD" ;;
        "paths.temp_prefix") var_name="TTS_PATHS_TEMP_PREFIX" ;;
        "paths.clipboard_prefix") var_name="TTS_PATHS_CLIPBOARD_PREFIX" ;;
        "features.enable_clipboard_debug") var_name="TTS_FEATURES_ENABLE_CLIPBOARD_DEBUG" ;;
        "features.enable_glass_sound") var_name="TTS_FEATURES_ENABLE_GLASS_SOUND" ;;
        "features.enable_log_rotation") var_name="TTS_FEATURES_ENABLE_LOG_ROTATION" ;;
        "features.log_rotation_size_kb") var_name="TTS_FEATURES_LOG_ROTATION_SIZE_KB" ;;
        "derived.target_min_chars") var_name="TTS_DERIVED_TARGET_MIN_CHARS" ;;
        "derived.target_max_chars") var_name="TTS_DERIVED_TARGET_MAX_CHARS" ;;
        "default.voice") var_name="TTS_PROFILE_DEFAULT_VOICE" ;;
        "default.rate_wpm") var_name="TTS_PROFILE_DEFAULT_RATE_WPM" ;;
        "default.volume") var_name="TTS_PROFILE_DEFAULT_VOLUME" ;;
        "default.pitch") var_name="TTS_PROFILE_DEFAULT_PITCH" ;;
        *) 
            if [[ -n "$default_value" ]]; then
                echo "$default_value"
                return 0
            else
                echo "ERROR: Configuration key not found: $key" >&2
                return 1
            fi
            ;;
    esac
    
    # Get the value from the environment variable
    local value="${!var_name}"
    if [[ -n "$value" ]]; then
        echo "$value"
        return 0
    fi
    
    # Return default value if provided
    if [[ -n "$default_value" ]]; then
        echo "$default_value"
        return 0
    fi
    
    echo "ERROR: Configuration key not found: $key" >&2
    return 1
}

# Validate configuration values
validate_config() {
    local errors=0
    
    # Validate speech rate
    local rate_wpm=$(get_config_value "speech.rate_wpm")
    if [[ ! "$rate_wpm" =~ ^[0-9]+$ ]] || [[ "$rate_wpm" -lt 80 ]] || [[ "$rate_wpm" -gt 500 ]]; then
        echo "ERROR: Invalid speech rate: $rate_wpm (must be 80-500 WPM)" >&2
        ((errors++))
    fi
    
    # Validate timing values
    local max_response=$(get_config_value "timing.max_full_response_seconds")
    if [[ ! "$max_response" =~ ^[0-9]+$ ]] || [[ "$max_response" -lt 1 ]]; then
        echo "ERROR: Invalid max full response seconds: $max_response" >&2
        ((errors++))
    fi
    
    # Validate required directories exist
    local debug_log=$(get_config_value "paths.debug_log")
    local debug_dir=$(dirname "$debug_log")
    if [[ ! -d "$debug_dir" ]]; then
        echo "ERROR: Debug log directory does not exist: $debug_dir" >&2
        ((errors++))
    fi
    
    return $errors
}

# Initialize configuration system
init_config() {
    load_tts_config || return $?
    load_speech_profiles
    validate_config || return $?
    
    echo "Configuration loaded successfully" >&2
    return 0
}

# Calculate derived values based on configuration
calculate_derived_config() {
    local chars_per_second=$(get_config_value "speech.chars_per_second")
    local target_min_seconds=$(get_config_value "timing.target_min_seconds")
    local target_max_seconds=$(get_config_value "timing.target_max_seconds")
    
    # Calculate character thresholds
    export TTS_DERIVED_TARGET_MIN_CHARS=$(echo "$target_min_seconds * $chars_per_second" | bc -l | awk '{printf "%.0f", $0}')
    export TTS_DERIVED_TARGET_MAX_CHARS=$(echo "$target_max_seconds * $chars_per_second" | bc -l | awk '{printf "%.0f", $0}')
}

# Export functions for use by other modules
export -f load_tts_config load_speech_profiles get_config_value validate_config init_config calculate_derived_config