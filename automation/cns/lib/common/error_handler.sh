#!/bin/bash

# Error Handler Module
# Provides standardized error reporting, recovery, and exit handling

# Source dependencies
source "$(dirname "${BASH_SOURCE[0]}")/logger.sh"

# Error codes (check if already set to avoid readonly errors)
if [[ -z "$ERR_SUCCESS" ]]; then
    readonly ERR_SUCCESS=0
    readonly ERR_GENERAL=1
    readonly ERR_FILE_NOT_FOUND=2
    readonly ERR_INVALID_JSON=3
    readonly ERR_CONFIG_ERROR=4
    readonly ERR_TIMEOUT=5
    readonly ERR_PERMISSION_DENIED=6
    readonly ERR_INVALID_INPUT=7
    readonly ERR_EXTERNAL_COMMAND=8
    readonly ERR_RESOURCE_EXHAUSTED=9
    readonly ERR_NETWORK_ERROR=10
fi

# Global error context (using regular variables for bash 3.x compatibility)
ERROR_MODULE=""
ERROR_OPERATION=""
ERROR_CONTEXT=""

# Get error description by code (using function instead of associative array)
get_error_description() {
    local error_code="$1"
    case "$error_code" in
        $ERR_SUCCESS) echo "Success" ;;
        $ERR_GENERAL) echo "General error" ;;
        $ERR_FILE_NOT_FOUND) echo "File not found" ;;
        $ERR_INVALID_JSON) echo "Invalid JSON format" ;;
        $ERR_CONFIG_ERROR) echo "Configuration error" ;;
        $ERR_TIMEOUT) echo "Operation timeout" ;;
        $ERR_PERMISSION_DENIED) echo "Permission denied" ;;
        $ERR_INVALID_INPUT) echo "Invalid input" ;;
        $ERR_EXTERNAL_COMMAND) echo "External command failed" ;;
        $ERR_RESOURCE_EXHAUSTED) echo "Resource exhausted" ;;
        $ERR_NETWORK_ERROR) echo "Network error" ;;
        *) echo "Unknown error" ;;
    esac
}

# Set error context for debugging
set_error_context() {
    ERROR_MODULE="$1"
    ERROR_OPERATION="$2"
    ERROR_CONTEXT="${3:-}"
}

# Handle error with context and logging
handle_error() {
    local error_code="$1"
    local error_message="$2"
    local should_exit="${3:-false}"
    
    local module="${ERROR_MODULE:-UNKNOWN}"
    local operation="${ERROR_OPERATION:-unknown_operation}"
    local context="${ERROR_CONTEXT:-}"
    
    # Get error description
    local description=$(get_error_description "$error_code")
    
    # Format full error message
    local full_message="[$description] $error_message"
    if [[ -n "$operation" ]]; then
        full_message="Operation '$operation': $full_message"
    fi
    if [[ -n "$context" ]]; then
        full_message="$full_message (Context: $context)"
    fi
    
    # Log the error
    log_error_with_context "$module" "$full_message" "$error_code"
    
    # Exit if requested
    if [[ "$should_exit" == "true" ]]; then
        cleanup_on_error "$error_code"
        exit "$error_code"
    fi
    
    return "$error_code"
}

# Handle file operation errors
handle_file_error() {
    local file_path="$1"
    local operation="$2"
    local should_exit="${3:-false}"
    
    if [[ ! -e "$file_path" ]]; then
        handle_error "$ERR_FILE_NOT_FOUND" "File does not exist: $file_path" "$should_exit"
    elif [[ ! -r "$file_path" ]]; then
        handle_error "$ERR_PERMISSION_DENIED" "Cannot read file: $file_path" "$should_exit"
    elif [[ "$operation" == "write" && ! -w "$file_path" ]]; then
        handle_error "$ERR_PERMISSION_DENIED" "Cannot write to file: $file_path" "$should_exit"
    else
        handle_error "$ERR_GENERAL" "File operation failed: $operation on $file_path" "$should_exit"
    fi
}

# Handle JSON parsing errors
handle_json_error() {
    local json_file="$1"
    local error_details="$2"
    local should_exit="${3:-false}"
    
    handle_error "$ERR_INVALID_JSON" "JSON parsing failed for $json_file: $error_details" "$should_exit"
}

# Handle configuration errors
handle_config_error() {
    local config_key="$1"
    local error_details="$2"
    local should_exit="${3:-false}"
    
    handle_error "$ERR_CONFIG_ERROR" "Configuration error for '$config_key': $error_details" "$should_exit"
}

# Handle timeout errors
handle_timeout_error() {
    local operation="$1"
    local timeout_seconds="$2"
    local should_exit="${3:-false}"
    
    handle_error "$ERR_TIMEOUT" "Operation '$operation' timed out after ${timeout_seconds}s" "$should_exit"
}

# Handle external command errors
handle_command_error() {
    local command="$1"
    local exit_code="$2"
    local output="$3"
    local should_exit="${4:-false}"
    
    local message="Command '$command' failed with exit code $exit_code"
    if [[ -n "$output" ]]; then
        message="$message. Output: $output"
    fi
    
    handle_error "$ERR_EXTERNAL_COMMAND" "$message" "$should_exit"
}

# Validate input and handle errors
validate_required_input() {
    local input_value="$1"
    local input_name="$2"
    local should_exit="${3:-false}"
    
    if [[ -z "$input_value" ]]; then
        handle_error "$ERR_INVALID_INPUT" "Required input missing: $input_name" "$should_exit"
        return "$ERR_INVALID_INPUT"
    fi
    
    return "$ERR_SUCCESS"
}

# Check if file exists and is readable
check_file_readable() {
    local file_path="$1"
    local file_description="${2:-file}"
    
    if [[ ! -f "$file_path" ]]; then
        handle_error "$ERR_FILE_NOT_FOUND" "$file_description not found: $file_path"
        return "$ERR_FILE_NOT_FOUND"
    fi
    
    if [[ ! -r "$file_path" ]]; then
        handle_error "$ERR_PERMISSION_DENIED" "Cannot read $file_description: $file_path"
        return "$ERR_PERMISSION_DENIED"
    fi
    
    return "$ERR_SUCCESS"
}

# Execute command with error handling
execute_with_error_handling() {
    local command="$1"
    local operation_name="$2"
    local timeout_seconds="${3:-30}"
    
    set_error_context "${ERROR_MODULE:-EXECUTOR}" "$operation_name"
    
    log_debug "EXECUTOR" "Executing command: $command"
    
    # Execute command with timeout
    local output
    local exit_code
    
    # Timeout command is required - fail immediately if not available
    if ! command -v timeout >/dev/null 2>&1; then
        handle_error "$ERR_EXTERNAL_COMMAND" "timeout command is required but not available on this system" true
    fi
    
    output=$(timeout "$timeout_seconds" bash -c "$command" 2>&1)
    exit_code=$?
    
    if [[ $exit_code -eq 124 ]]; then
        handle_timeout_error "$operation_name" "$timeout_seconds"
        return "$ERR_TIMEOUT"
    fi
    
    if [[ $exit_code -ne 0 ]]; then
        handle_command_error "$command" "$exit_code" "$output"
        return "$ERR_EXTERNAL_COMMAND"
    fi
    
    log_debug "EXECUTOR" "Command completed successfully: $command"
    echo "$output"
    return "$ERR_SUCCESS"
}

# Cleanup function for error scenarios
cleanup_on_error() {
    local error_code="$1"
    
    log_info "CLEANUP" "Performing error cleanup (error code: $error_code)"
    
    # Remove temporary files - fail immediately if config cannot be read or cleanup fails
    local temp_prefix=$(get_config_value "paths.temp_prefix" "/tmp/claude_speech_")
    if [[ -n "$temp_prefix" ]]; then
        find /tmp -name "${temp_prefix##*/}*" -type f -mmin -60 -delete
        if [[ $? -ne 0 ]]; then
            handle_error "$ERR_GENERAL" "Failed to cleanup temporary files with prefix: $temp_prefix"
        fi
    fi
    
    # Kill any background processes if needed
    # This could be expanded based on specific cleanup needs
    
    log_info "CLEANUP" "Error cleanup completed"
}

# Set up error trap for the script
setup_error_trap() {
    set -E  # Enable error trapping in functions
    
    trap 'handle_error $? "Unexpected error in ${FUNCNAME[1]:-main} at line ${BASH_LINENO[0]}" true' ERR
    trap 'cleanup_on_error 1' EXIT
}

# Disable error trap (for controlled exit)
disable_error_trap() {
    trap - ERR EXIT
}


# Export functions for use by other modules
export -f set_error_context handle_error handle_file_error handle_json_error handle_config_error
export -f handle_timeout_error handle_command_error validate_required_input check_file_readable
export -f execute_with_error_handling cleanup_on_error setup_error_trap disable_error_trap
export -f get_error_description

# Export error constants
export ERR_SUCCESS ERR_GENERAL ERR_FILE_NOT_FOUND ERR_INVALID_JSON ERR_CONFIG_ERROR ERR_TIMEOUT
export ERR_PERMISSION_DENIED ERR_INVALID_INPUT ERR_EXTERNAL_COMMAND ERR_RESOURCE_EXHAUSTED ERR_NETWORK_ERROR