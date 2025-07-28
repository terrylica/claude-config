#!/bin/bash

# CNS Configuration Loader Module
# Simplified configuration loader for CNS (Conversation Notification System)
# Handles clipboard tracking and glass sound notifications only

# Configuration file paths
readonly CNS_CONFIG_DIR="/Users/terryli/.claude/automation/cns/config"
readonly CNS_CONFIG_FILE="$CNS_CONFIG_DIR/cns_config.json"

# Load CNS configuration
load_cns_config() {
    local config_file="${1:-$CNS_CONFIG_FILE}"
    
    if [[ ! -f "$config_file" ]]; then
        echo "ERROR: CNS config file not found: $config_file" >&2
        return 1
    fi
    
    if ! jq empty "$config_file" 2>/dev/null; then
        echo "ERROR: Invalid JSON in CNS config file: $config_file" >&2
        return 2  
    fi
    
    # Load CNS-specific settings
    export CNS_DEBUG_LOG=$(jq -r '.paths.debug_log // "/tmp/claude_cns_debug.log"' "$config_file")
    export CNS_DEBUG_LOG_OLD=$(jq -r '.paths.debug_log_old // "/tmp/claude_cns_debug.log.old"' "$config_file")
    
    export CNS_ENABLE_CLIPBOARD_DEBUG=$(jq -r '.features.enable_clipboard_debug // true' "$config_file")
    export CNS_ENABLE_GLASS_SOUND=$(jq -r '.features.enable_glass_sound // true' "$config_file")
    export CNS_ENABLE_LOG_ROTATION=$(jq -r '.features.enable_log_rotation // true' "$config_file")
    export CNS_LOG_ROTATION_SIZE_KB=$(jq -r '.features.log_rotation_size_kb // 50' "$config_file")
    
    return 0
}

# Get configuration value by key path
get_config_value() {
    local key_path="$1"
    local default_value="$2"
    local config_file="${3:-$CNS_CONFIG_FILE}"
    
    if [[ ! -f "$config_file" ]]; then
        echo "$default_value"
        return 1
    fi
    
    local value=$(jq -r ".$key_path // \"$default_value\"" "$config_file" 2>/dev/null)
    echo "$value"
}

# Initialize CNS configuration
init_config() {
    load_cns_config || return $?
    return 0
}

# Export functions for use by other modules
export -f load_cns_config get_config_value init_config