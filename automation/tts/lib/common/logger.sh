#!/bin/bash

# Logging Infrastructure Module
# Provides structured logging with levels, timestamps, and rotation

# Source configuration loader
source "$(dirname "${BASH_SOURCE[0]}")/config_loader.sh"

# Log levels (check if already set to avoid readonly errors)
if [[ -z "$LOG_LEVEL_DEBUG" ]]; then
    readonly LOG_LEVEL_DEBUG=0
    readonly LOG_LEVEL_INFO=1
    readonly LOG_LEVEL_WARN=2
    readonly LOG_LEVEL_ERROR=3
fi

# Current log level (loaded from config)
LOG_LEVEL="$LOG_LEVEL_INFO"

# Log file path (loaded from config)
LOG_FILE="/tmp/claude_tts_debug.log"

# Initialize logging system
init_logging() {
    # Load log file path from configuration
    LOG_FILE=$(get_config_value "paths.debug_log" "/tmp/claude_tts_debug.log")
    
    # Set log level based on configuration
    local config_level=$(get_config_value "logging.level" "INFO")
    case "$config_level" in
        "DEBUG") LOG_LEVEL=$LOG_LEVEL_DEBUG ;;
        "INFO")  LOG_LEVEL=$LOG_LEVEL_INFO ;;
        "WARN")  LOG_LEVEL=$LOG_LEVEL_WARN ;;
        "ERROR") LOG_LEVEL=$LOG_LEVEL_ERROR ;;
        *) LOG_LEVEL=$LOG_LEVEL_INFO ;;
    esac
    
    # Perform log rotation if needed
    rotate_log_if_needed
}

# Rotate log file if it exceeds size limit
rotate_log_if_needed() {
    local rotation_enabled=$(get_config_value "features.enable_log_rotation" "true")
    local max_size_kb=$(get_config_value "features.log_rotation_size_kb" "50")
    
    if [[ "$rotation_enabled" == "true" && -f "$LOG_FILE" ]]; then
        local current_size_bytes=$(stat -f%z "$LOG_FILE" 2>/dev/null || echo 0)
        local max_size_bytes=$((max_size_kb * 1024))
        
        if [[ "$current_size_bytes" -gt "$max_size_bytes" ]]; then
            local old_log=$(get_config_value "paths.debug_log_old" "${LOG_FILE}.old")
            mv "$LOG_FILE" "$old_log"
            log_info "LOGGER" "Log rotated: $LOG_FILE -> $old_log"
        fi
    fi
}

# Core logging function
log_message() {
    local level="$1"
    local level_num="$2"
    local module="$3"
    local message="$4"
    
    # Check if we should log this level
    if [[ "$level_num" -lt "$LOG_LEVEL" ]]; then
        return 0
    fi
    
    # Format timestamp
    local timestamp=$(date "+%a %d %b %Y %H:%M:%S %Z")
    
    # Format log entry
    local log_entry="$timestamp [$level] [$module] $message"
    
    # Write to log file
    echo "$log_entry" >> "$LOG_FILE"
    
    # Also output to stderr for errors and warnings
    if [[ "$level_num" -ge "$LOG_LEVEL_WARN" ]]; then
        echo "$log_entry" >&2
    fi
}

# Convenience logging functions
log_debug() {
    local module="$1"
    local message="$2"
    log_message "DEBUG" "$LOG_LEVEL_DEBUG" "$module" "$message"
}

log_info() {
    local module="$1"
    local message="$2"
    log_message "INFO" "$LOG_LEVEL_INFO" "$module" "$message"
}

log_warn() {
    local module="$1"
    local message="$2"
    log_message "WARN" "$LOG_LEVEL_WARN" "$module" "$message"
}

log_error() {
    local module="$1"
    local message="$2"
    log_message "ERROR" "$LOG_LEVEL_ERROR" "$module" "$message"
}

# Log with context (session ID, process info)
log_with_context() {
    local level="$1"
    local module="$2"
    local message="$3"
    local session_id="${4:-}"
    
    local context_info=""
    if [[ -n "$session_id" ]]; then
        context_info="[Session: ${session_id:0:8}...] "
    fi
    
    # Add process info if enabled in config
    local include_process=$(get_config_value "logging.include_process_info" "true")
    if [[ "$include_process" == "true" ]]; then
        context_info="${context_info}[PID: $$] "
    fi
    
    case "$level" in
        "DEBUG") log_debug "$module" "${context_info}$message" ;;
        "INFO")  log_info "$module" "${context_info}$message" ;;
        "WARN")  log_warn "$module" "${context_info}$message" ;;
        "ERROR") log_error "$module" "${context_info}$message" ;;
    esac
}

# Log hook event details
log_hook_event() {
    local session_id="$1"
    local transcript_path="$2"
    local hook_event_name="$3"
    local cwd="$4"
    
    log_info "HOOK" "=== HOOK EVENT DETAILS ==="
    log_info "HOOK" "Session ID: $session_id"
    log_info "HOOK" "Transcript path: $transcript_path"
    log_info "HOOK" "Hook event name: $hook_event_name"
    log_info "HOOK" "Working directory: $cwd"
    log_info "HOOK" "========================="
}

# Log performance metrics
log_performance() {
    local module="$1"
    local operation="$2"
    local duration_seconds="$3"
    local additional_info="${4:-}"
    
    local message="Operation '$operation' completed in ${duration_seconds}s"
    if [[ -n "$additional_info" ]]; then
        message="$message ($additional_info)"
    fi
    
    log_info "$module" "$message"
}

# Log error with stack trace context
log_error_with_context() {
    local module="$1"
    local error_message="$2"
    local exit_code="${3:-1}"
    
    log_error "$module" "ERROR: $error_message"
    log_error "$module" "Exit code: $exit_code"
    log_error "$module" "Function: ${FUNCNAME[1]}"
    log_error "$module" "Script: ${BASH_SOURCE[1]}"
    log_error "$module" "Line: ${BASH_LINENO[0]}"
}

# Export functions for use by other modules
export -f init_logging rotate_log_if_needed log_message log_debug log_info log_warn log_error
export -f log_with_context log_hook_event log_performance log_error_with_context