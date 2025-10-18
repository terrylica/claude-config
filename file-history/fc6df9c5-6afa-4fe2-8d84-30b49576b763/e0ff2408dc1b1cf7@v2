-- validation.ddb - Universal Indicator Validation Schema
-- Version: 1.0.0
-- Created: 2025-10-16
-- Purpose: Track validation runs and store MQL5 vs Python correlation metrics

-- Validation runs table
CREATE TABLE IF NOT EXISTS validation_runs (
    run_id INTEGER PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    indicator_name VARCHAR NOT NULL,
    symbol VARCHAR NOT NULL,
    timeframe VARCHAR NOT NULL,
    bars INTEGER NOT NULL,
    mql5_csv_path VARCHAR NOT NULL,
    python_version VARCHAR NOT NULL,
    status VARCHAR NOT NULL CHECK (status IN ('pending', 'running', 'success', 'failed')),
    error_message VARCHAR
);

-- Buffer validation metrics table
CREATE TABLE IF NOT EXISTS buffer_metrics (
    metric_id INTEGER PRIMARY KEY,
    run_id INTEGER NOT NULL REFERENCES validation_runs(run_id),
    buffer_name VARCHAR NOT NULL,
    correlation DOUBLE NOT NULL,
    mae DOUBLE NOT NULL,
    rmse DOUBLE NOT NULL,
    max_diff DOUBLE NOT NULL,
    mql5_min DOUBLE NOT NULL,
    mql5_max DOUBLE NOT NULL,
    mql5_mean DOUBLE NOT NULL,
    python_min DOUBLE NOT NULL,
    python_max DOUBLE NOT NULL,
    python_mean DOUBLE NOT NULL,
    pass BOOLEAN NOT NULL,
    UNIQUE(run_id, buffer_name)
);

-- Bar-level differences table (for debugging mismatches)
CREATE TABLE IF NOT EXISTS bar_diffs (
    diff_id INTEGER PRIMARY KEY,
    run_id INTEGER NOT NULL REFERENCES validation_runs(run_id),
    buffer_name VARCHAR NOT NULL,
    bar_index INTEGER NOT NULL,
    bar_time TIMESTAMP NOT NULL,
    mql5_value DOUBLE NOT NULL,
    python_value DOUBLE NOT NULL,
    diff DOUBLE NOT NULL,
    abs_diff DOUBLE NOT NULL,
    UNIQUE(run_id, buffer_name, bar_index)
);

-- Indicator parameters table (for reproducibility)
CREATE TABLE IF NOT EXISTS indicator_parameters (
    param_id INTEGER PRIMARY KEY,
    run_id INTEGER NOT NULL REFERENCES validation_runs(run_id),
    param_name VARCHAR NOT NULL,
    param_value VARCHAR NOT NULL,
    UNIQUE(run_id, param_name)
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_validation_runs_timestamp ON validation_runs(timestamp);
CREATE INDEX IF NOT EXISTS idx_validation_runs_indicator ON validation_runs(indicator_name);
CREATE INDEX IF NOT EXISTS idx_validation_runs_status ON validation_runs(status);
CREATE INDEX IF NOT EXISTS idx_buffer_metrics_run_id ON buffer_metrics(run_id);
CREATE INDEX IF NOT EXISTS idx_buffer_metrics_pass ON buffer_metrics(pass);
CREATE INDEX IF NOT EXISTS idx_bar_diffs_run_id ON bar_diffs(run_id);
CREATE INDEX IF NOT EXISTS idx_bar_diffs_abs_diff ON bar_diffs(abs_diff);
CREATE INDEX IF NOT EXISTS idx_indicator_parameters_run_id ON indicator_parameters(run_id);

-- View: Latest validation results per indicator
CREATE OR REPLACE VIEW latest_validations AS
SELECT
    vr.run_id,
    vr.timestamp,
    vr.indicator_name,
    vr.symbol,
    vr.timeframe,
    vr.bars,
    vr.status,
    COUNT(bm.metric_id) AS total_buffers,
    SUM(CASE WHEN bm.pass THEN 1 ELSE 0 END) AS passed_buffers,
    MIN(bm.correlation) AS min_correlation,
    MAX(bm.max_diff) AS max_diff
FROM validation_runs vr
LEFT JOIN buffer_metrics bm ON vr.run_id = bm.run_id
WHERE vr.run_id IN (
    SELECT MAX(run_id)
    FROM validation_runs
    GROUP BY indicator_name, symbol, timeframe
)
GROUP BY vr.run_id, vr.timestamp, vr.indicator_name, vr.symbol, vr.timeframe, vr.bars, vr.status
ORDER BY vr.timestamp DESC;

-- View: Failed validations requiring attention
CREATE OR REPLACE VIEW failed_validations AS
SELECT
    vr.run_id,
    vr.timestamp,
    vr.indicator_name,
    vr.symbol,
    vr.timeframe,
    bm.buffer_name,
    bm.correlation,
    bm.max_diff,
    vr.error_message
FROM validation_runs vr
INNER JOIN buffer_metrics bm ON vr.run_id = bm.run_id
WHERE bm.pass = FALSE OR vr.status = 'failed'
ORDER BY vr.timestamp DESC, bm.correlation ASC;

-- View: Correlation summary by indicator
CREATE OR REPLACE VIEW indicator_summary AS
SELECT
    vr.indicator_name,
    COUNT(DISTINCT vr.run_id) AS total_runs,
    SUM(CASE WHEN vr.status = 'success' THEN 1 ELSE 0 END) AS successful_runs,
    MIN(bm.correlation) AS worst_correlation,
    AVG(bm.correlation) AS avg_correlation,
    MAX(bm.max_diff) AS worst_diff
FROM validation_runs vr
LEFT JOIN buffer_metrics bm ON vr.run_id = bm.run_id
GROUP BY vr.indicator_name
ORDER BY worst_correlation ASC;
