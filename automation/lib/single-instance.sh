#!/usr/bin/env bash
# Single-Instance Protection Library
# Prevents multiple instances of the same script from running simultaneously
# Version: 1.0.0

# Usage:
#   source /path/to/single-instance.sh
#   ensure_single_instance "script-name" [--kill-existing]
#
# Features:
# - PID file management with stale PID cleanup
# - File locking (flock) for atomic operations
# - Process verification (not just PID file check)
# - Automatic cleanup on exit
# - Optional: kill existing instances

set -euo pipefail

# Configuration
PIDFILE_DIR="${PIDFILE_DIR:-$HOME/.claude/automation/run}"
LOCK_TIMEOUT=5  # seconds to wait for lock

# Ensure PID directory exists
mkdir -p "$PIDFILE_DIR"

# Check if a PID is actually running
is_process_running() {
    local pid="$1"

    # Check if PID exists
    if ! ps -p "$pid" > /dev/null 2>&1; then
        return 1
    fi

    return 0
}

# Check if a PID belongs to our script
is_our_process() {
    local pid="$1"
    local script_name="$2"

    # Get process command
    local cmd
    cmd=$(ps -p "$pid" -o command= 2>/dev/null || echo "")

    # Check if command contains our script name
    if [[ "$cmd" == *"$script_name"* ]]; then
        return 0
    fi

    return 1
}

# Clean up stale PID file
cleanup_stale_pidfile() {
    local pidfile="$1"
    local script_name="$2"

    if [[ ! -f "$pidfile" ]]; then
        return 0
    fi

    local old_pid
    old_pid=$(cat "$pidfile" 2>/dev/null || echo "")

    if [[ -z "$old_pid" ]]; then
        # Empty PID file - remove it
        rm -f "$pidfile"
        return 0
    fi

    # Check if process is running
    if ! is_process_running "$old_pid"; then
        # Process not running - stale PID file
        echo "[single-instance] Removing stale PID file (PID $old_pid not running)" >&2
        rm -f "$pidfile"
        return 0
    fi

    # Process exists - verify it's actually our script
    if ! is_our_process "$old_pid" "$script_name"; then
        # PID reused by different process
        echo "[single-instance] Removing stale PID file (PID $old_pid is different process)" >&2
        rm -f "$pidfile"
        return 0
    fi

    # Process is running and is our script
    return 1
}

# Kill existing instance
kill_existing_instance() {
    local pidfile="$1"
    local script_name="$2"

    if [[ ! -f "$pidfile" ]]; then
        return 0
    fi

    local old_pid
    old_pid=$(cat "$pidfile" 2>/dev/null || echo "")

    if [[ -z "$old_pid" ]]; then
        rm -f "$pidfile"
        return 0
    fi

    # Verify it's our process before killing
    if is_process_running "$old_pid" && is_our_process "$old_pid" "$script_name"; then
        echo "[single-instance] Killing existing instance (PID $old_pid)" >&2
        kill -TERM "$old_pid" 2>/dev/null || true

        # Wait up to 5 seconds for graceful termination
        local wait_count=0
        while is_process_running "$old_pid" && [[ $wait_count -lt 50 ]]; do
            sleep 0.1
            wait_count=$((wait_count + 1))
        done

        # Force kill if still running
        if is_process_running "$old_pid"; then
            echo "[single-instance] Force killing instance (PID $old_pid)" >&2
            kill -9 "$old_pid" 2>/dev/null || true
            sleep 0.5
        fi
    fi

    rm -f "$pidfile"
}

# Cleanup function to remove PID file on exit
cleanup_pidfile() {
    local pidfile="$1"
    rm -f "$pidfile" 2>/dev/null || true
}

# Main function: Ensure single instance
ensure_single_instance() {
    local script_name="$1"
    local kill_existing=false

    # Parse options
    shift
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --kill-existing)
                kill_existing=true
                shift
                ;;
            *)
                echo "[single-instance] Unknown option: $1" >&2
                return 1
                ;;
        esac
    done

    # Sanitize script name for filename
    local safe_name
    safe_name=$(echo "$script_name" | tr '/' '_' | tr ' ' '_')

    local pidfile="$PIDFILE_DIR/${safe_name}.pid"
    local lockfile="$PIDFILE_DIR/${safe_name}.lock"

    # Use atomic mkdir for locking (macOS compatible)
    local lock_acquired=false
    local attempts=0
    local max_attempts=$((LOCK_TIMEOUT * 10))  # 10 attempts per second

    while [[ $attempts -lt $max_attempts ]]; do
        if mkdir "$lockfile" 2>/dev/null; then
            lock_acquired=true
            break
        fi
        sleep 0.1
        attempts=$((attempts + 1))
    done

    if [[ "$lock_acquired" != "true" ]]; then
        echo "[single-instance] ERROR: Failed to acquire lock for $script_name after ${LOCK_TIMEOUT}s" >&2
        return 1
    fi

    # Ensure lock cleanup
    trap "rmdir '$lockfile' 2>/dev/null || true" EXIT TERM INT

    # Clean up stale PID file or kill existing instance
    if [[ "$kill_existing" == "true" ]]; then
        kill_existing_instance "$pidfile" "$script_name"
    else
        if ! cleanup_stale_pidfile "$pidfile" "$script_name"; then
            local old_pid
            old_pid=$(cat "$pidfile" 2>/dev/null || echo "unknown")
            rmdir "$lockfile" 2>/dev/null || true
            echo "[single-instance] ERROR: $script_name is already running (PID $old_pid)" >&2
            echo "[single-instance] Use --kill-existing to terminate existing instance" >&2
            return 1
        fi
    fi

    # Write our PID
    echo "$$" > "$pidfile"

    # Release lock
    rmdir "$lockfile" 2>/dev/null || true

    # Register cleanup on exit
    trap "cleanup_pidfile '$pidfile'" EXIT TERM INT

    echo "[single-instance] Started $script_name with PID $$" >&2
    return 0
}

# Alternative: Quick check without enforcement (useful for hooks)
check_instance_count() {
    local script_pattern="$1"
    local max_instances="${2:-1}"

    # Count running instances (excluding grep and current shell)
    local count
    count=$(pgrep -f "$script_pattern" | wc -l | tr -d ' ')

    echo "$count"
}

# Kill all instances matching pattern
kill_all_instances() {
    local script_pattern="$1"

    echo "[single-instance] Killing all instances matching: $script_pattern" >&2
    pkill -TERM -f "$script_pattern" 2>/dev/null || true
    sleep 1

    # Force kill any remaining
    if pgrep -f "$script_pattern" > /dev/null 2>&1; then
        echo "[single-instance] Force killing remaining instances" >&2
        pkill -9 -f "$script_pattern" 2>/dev/null || true
    fi
}
