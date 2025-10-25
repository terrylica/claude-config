-- Migration: Create event store
-- Version: 001
-- Description: SQLite event store for multi-workspace session tracking
-- SLO: Correctness 100% (all events captured, no silent failures)

-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Enable WAL mode for better concurrency
PRAGMA journal_mode = WAL;

-- Session events table
CREATE TABLE IF NOT EXISTS session_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    correlation_id TEXT NOT NULL,
    workspace_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    component TEXT NOT NULL CHECK (component IN ('hook', 'bot', 'orchestrator', 'claude-cli')),
    event_type TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    metadata JSON,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc'))
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_correlation ON session_events(correlation_id);
CREATE INDEX IF NOT EXISTS idx_workspace_time ON session_events(workspace_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_session ON session_events(session_id);
CREATE INDEX IF NOT EXISTS idx_component_type ON session_events(component, event_type);
CREATE INDEX IF NOT EXISTS idx_timestamp ON session_events(timestamp DESC);

-- Schema migrations tracking
CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (datetime('now', 'utc'))
);

-- Record this migration
INSERT OR IGNORE INTO schema_migrations (version) VALUES ('001');
