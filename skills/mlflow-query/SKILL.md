---
name: mlflow-query
description: Query MLflow tracking server for experiment runs, metrics, parameters, and artifacts. Use when searching for best models, comparing experiments, detecting overfitting, analyzing training metrics, filtering by hyperparameters, or exporting run data. Triggers - mlflow, experiment, runs, metrics, parameters, artifacts, model performance, training history, hyperparameter search, overfitting detection.
allowed-tools: Read, Bash, Grep, Glob
---

# MLflow Query Skill

**Query and analyze MLflow experiment tracking data within defined boundaries.**

---

## ⚠️ Skill Activation - What Can I Help You With?

**You've activated the MLflow Query skill. Before we proceed, let me explain what I can and cannot do:**

### ✅ What This Skill CAN Do (Within Boundaries)

**Read-Only Query Operations:**

1. **Find Best Models** - Search experiments and rank by metrics (accuracy, loss, custom metrics)
2. **Compare Runs** - Side-by-side comparison of hyperparameters and metrics
3. **Filter Runs** - Filter by metrics, parameters, tags, status (AND-only filters)
4. **Export Data** - Export run data to CSV/JSON for analysis
5. **Detect Issues** - Identify overfitting (train vs test gaps), failed runs, anomalies
6. **List Resources** - Show experiments, runs, artifacts available

**Available Commands:**

- `mlflow experiments search` - List all experiments
- `mlflow runs list --experiment-id <id>` - List runs in experiment
- `mlflow runs describe --run-id <id>` - Get complete run details (JSON)
- `mlflow experiments csv --experiment-id <id>` - Export all runs to CSV
- `mlflow artifacts list --run-id <id>` - List artifacts for a run

**Credential Management:**

- Doppler integration (zero-exposure credentials)
- Environment variable injection
- Remote tracking server authentication

### ❌ What This Skill CANNOT Do (Outside Boundaries)

**Write Operations (Blocked by Design):**

- ❌ Create, modify, or delete runs/experiments
- ❌ Upload artifacts
- ❌ Update tags or parameters
- ❌ Start training runs

**Technical Limitations (MLflow Constraints):**

- ❌ OR filters (only AND filters supported: `metric > 0.8 AND param = 'value'`)
- ❌ Streaming/real-time results (poll-based only, use pagination)
- ❌ Aggregation in queries (no SUM, AVG, COUNT in filters - do client-side)
- ❌ Parameter arithmetic in filters (params are strings, need workarounds)
- ❌ Metric history via CLI (use Python API for time-series)

**Security Restrictions:**

- ❌ Hardcoded credentials (must use Doppler or env vars)
- ❌ Network exfiltration (WebFetch blocked by allowed-tools)
- ❌ Arbitrary code execution

---

## 🎯 How Would You Like to Proceed?

**Choose a workflow below, or ask a specific question:**

### Common Tasks (Select One)

**A. Find Best Performing Model**

- Input needed: Experiment ID, metric name (e.g., "accuracy", "loss")
- Output: Run ID, metric value, hyperparameters
- Time: ~2 minutes

**B. Compare Multiple Runs**

- Input needed: List of run IDs or experiment ID + filter criteria
- Output: Side-by-side comparison table
- Time: ~3 minutes

**C. Detect Overfitting**

- Input needed: Experiment ID, train metric name, test metric name
- Output: Runs with large train/test gaps, recommendations
- Time: ~5 minutes

**D. Export Experiment Data**

- Input needed: Experiment ID, output format (CSV/JSON)
- Output: File with all runs, metrics, parameters
- Time: ~2 minutes

**E. Filter Runs by Criteria**

- Input needed: Experiment ID, filter conditions (AND-only)
- Output: Matching runs list
- Time: ~3 minutes
- Example filters: `metrics.accuracy > 0.9 AND params.model = 'transformer'`

**F. List Available Resources**

- Input needed: None (or experiment ID for runs)
- Output: Experiments list or runs list
- Time: ~1 minute

**G. Custom Query**

- Describe what you're looking for, I'll guide you through available options

---

## 📋 Prerequisites Check

Before proceeding, verify these requirements:

**1. MLflow CLI Installed**

```bash
which mlflow || echo "Install: pip install mlflow"
```

**2. Tracking Server Access**

Choose one credential method:

**Option A: Doppler (Recommended - Zero Exposure)**

```bash
# Verify Doppler secrets exist
doppler secrets --project claude-config --config dev | grep MLFLOW
```

Required secrets:

- `MLFLOW_HOST` (e.g., mlflow.eonlabs.com)
- `MLFLOW_PORT` (e.g., 5000)
- `MLFLOW_USERNAME` (e.g., eonlabs)
- `MLFLOW_PASSWORD` (secure password)

**Option B: Environment Variable**

```bash
export MLFLOW_TRACKING_URI="http://localhost:5000"
# Or for remote with auth:
export MLFLOW_TRACKING_URI="http://user:pass@mlflow.example.com:5000"
```

**3. Connection Test**

```bash
# With Doppler
doppler run --project claude-config --config dev -- bash -c \
  'export MLFLOW_TRACKING_URI="http://$MLFLOW_USERNAME:$MLFLOW_PASSWORD@$MLFLOW_HOST:$MLFLOW_PORT" && \
   uvx mlflow experiments search' | head -5

# With env var
uvx mlflow experiments search | head -5
```

**Expected**: List of experiments (not an error)

---

## 🔧 Understanding Constraints (MLflow Limitations)

### Constraint 1: AND-Only Filters (No OR)

**❌ This WILL NOT work:**

```bash
mlflow runs search --filter-string "params.status = 'prod' OR params.status = 'staging'"
# Error: Invalid clause(s) in filter string: 'OR'
```

**✅ Workaround - Multiple Queries:**

```bash
# Query 1: Production runs
mlflow runs search --filter-string "params.status = 'prod'" > prod_runs.txt

# Query 2: Staging runs
mlflow runs search --filter-string "params.status = 'staging'" > staging_runs.txt

# Merge results client-side
cat prod_runs.txt staging_runs.txt
```

### Constraint 2: Parameters Are Always Strings

**❌ This WILL NOT work:**

```bash
mlflow runs search --filter-string "params.learning_rate > 0.001"
# Error: Type mismatch (comparing string to number)
```

**✅ Workaround - Quote Values:**

```bash
# Exact match (works)
mlflow runs search --filter-string "params.learning_rate = '0.001'"

# Range queries (need client-side filtering)
mlflow runs search --experiment-id 1 | \
  grep learning_rate | \
  awk -F'|' '$3 > 0.001 {print}'
```

### Constraint 3: No Streaming (Use Pagination)

**❌ No real-time updates:**

```bash
# This returns static snapshot, not live stream
mlflow runs search --experiment-id 1
```

**✅ Workaround - Paginate Large Results:**

```bash
# Get first 100
mlflow runs search --experiment-id 1 --max-results 100

# For more, export to CSV (efficient for large datasets)
mlflow experiments csv --experiment-id 1 --filename results.csv
```

### Constraint 4: Metric History Requires Python API

**❌ CLI doesn't support time-series:**

```bash
# No CLI command for metric history over training steps
```

**✅ Workaround - Python Script:**

```python
#!/usr/bin/env python3
# /// script
# dependencies = ["mlflow>=2.9.0"]
# ///
from mlflow.tracking import MlflowClient

client = MlflowClient()
history = client.get_metric_history(run_id="<RUN_ID>", key="loss")
for entry in history:
    print(f"Step {entry.step}: {entry.value}")
```

Usage: `uv run get_history.py`

---

## 📖 Common Workflows (Guided)

### Workflow A: Find Best Performing Model

**Input Questions:**

1. What experiment ID? (or experiment name)
2. What metric to optimize? (e.g., accuracy, f1_score, loss)
3. Higher is better or lower is better?

**Example:**

```bash
# User inputs:
# - Experiment ID: 1
# - Metric: accuracy
# - Direction: higher is better

# Step 1: List runs ordered by metric
doppler run --project claude-config --config dev -- bash -c \
  'export MLFLOW_TRACKING_URI="http://$MLFLOW_USERNAME:$MLFLOW_PASSWORD@$MLFLOW_HOST:$MLFLOW_PORT" && \
   uvx mlflow runs list --experiment-id 1' | \
  grep -E "accuracy|run_id" | \
  head -10

# Step 2: Get full details of best run
# (Extract run_id from above, e.g., abc123)
doppler run --project claude-config --config dev -- bash -c \
  'export MLFLOW_TRACKING_URI="http://$MLFLOW_USERNAME:$MLFLOW_PASSWORD@$MLFLOW_HOST:$MLFLOW_PORT" && \
   uvx mlflow runs describe --run-id abc123'
```

**Output:**

- Run ID
- Accuracy value
- All hyperparameters
- Model artifacts location

### Workflow B: Compare Multiple Runs

**Input Questions:**

1. What experiment ID?
2. What run IDs to compare? (or filter criteria)
3. What fields to compare? (metrics/params/both)

**Example:**

```bash
# User inputs:
# - Experiment ID: 1
# - Run IDs: abc123, def456, ghi789
# - Fields: metrics.accuracy, params.learning_rate, params.batch_size

# Export to CSV for easy comparison
doppler run --project claude-config --config dev -- bash -c \
  'export MLFLOW_TRACKING_URI="http://$MLFLOW_USERNAME:$MLFLOW_PASSWORD@$MLFLOW_HOST:$MLFLOW_PORT" && \
   uvx mlflow experiments csv --experiment-id 1 --filename /tmp/exp1.csv'

# Filter specific runs
grep -E "abc123|def456|ghi789" /tmp/exp1.csv | \
  awk -F',' '{print $1, $5, $8, $9}'  # Adjust columns as needed
```

### Workflow C: Detect Overfitting

**Input Questions:**

1. What experiment ID?
2. What train metric? (e.g., train_accuracy)
3. What test metric? (e.g., test_accuracy)
4. What gap threshold? (default: 0.05 = 5%)

**Example:**

```bash
# User inputs:
# - Experiment ID: 1
# - Train metric: train_accuracy
# - Test metric: test_accuracy
# - Threshold: 0.05 (5% gap = overfitting)

# Export all runs
doppler run --project claude-config --config dev -- bash -c \
  'export MLFLOW_TRACKING_URI="http://$MLFLOW_USERNAME:$MLFLOW_PASSWORD@$MLFLOW_HOST:$MLFLOW_PORT" && \
   uvx mlflow experiments csv --experiment-id 1 --filename /tmp/exp1.csv'

# Analyze gaps (awk calculation)
awk -F',' 'NR>1 {
  train=$5; test=$6;  # Adjust column numbers
  gap=train-test;
  if (gap > 0.05) print $1, "Overfitting:", gap
}' /tmp/exp1.csv
```

**Output:**

- Run IDs with overfitting
- Train-test gap values
- Recommendations

### Workflow D: Export Experiment Data

**Input Questions:**

1. What experiment ID?
2. Output format? (CSV recommended for large data)
3. Output location? (default: /tmp/)

**Example:**

```bash
# User inputs:
# - Experiment ID: 1
# - Format: CSV
# - Location: /tmp/crypto_backtest.csv

doppler run --project claude-config --config dev -- bash -c \
  'export MLFLOW_TRACKING_URI="http://$MLFLOW_USERNAME:$MLFLOW_PASSWORD@$MLFLOW_HOST:$MLFLOW_PORT" && \
   uvx mlflow experiments csv --experiment-id 1 --filename /tmp/crypto_backtest.csv'

# Verify
wc -l /tmp/crypto_backtest.csv
head -3 /tmp/crypto_backtest.csv
```

### Workflow E: Filter Runs by Criteria

**Input Questions:**

1. What experiment ID?
2. Filter conditions? (AND-only, examples provided)
3. How many results? (default: all)

**Valid filter patterns:**

```bash
# Metric filters (use actual metric values)
"metrics.accuracy > 0.9"
"metrics.loss < 0.1"

# Parameter filters (MUST quote values - params are strings!)
"params.model = 'transformer'"
"params.learning_rate = '0.001'"

# Tag filters
"tags.status = 'production'"

# Status filters
"attributes.status = 'FINISHED'"

# Combined (AND-only)
"metrics.accuracy > 0.9 AND params.model = 'transformer'"
```

**Example:**

```bash
# User inputs:
# - Experiment ID: 1
# - Filter: metrics.accuracy > 0.9 AND params.model = 'transformer'

# Note: runs search doesn't support --filter-string, use runs list
doppler run --project claude-config --config dev -- bash -c \
  'export MLFLOW_TRACKING_URI="http://$MLFLOW_USERNAME:$MLFLOW_PASSWORD@$MLFLOW_HOST:$MLFLOW_PORT" && \
   uvx mlflow runs list --experiment-id 1' | \
  grep transformer | \
  grep -E "accuracy.*0.9[0-9]"  # Adjust pattern for metric values
```

**Note**: For complex filters, export to CSV and use awk/python.

### Workflow F: List Available Resources

**No input needed** - Just explores what's available.

**Example:**

```bash
# List all experiments
doppler run --project claude-config --config dev -- bash -c \
  'export MLFLOW_TRACKING_URI="http://$MLFLOW_USERNAME:$MLFLOW_PASSWORD@$MLFLOW_HOST:$MLFLOW_PORT" && \
   uvx mlflow experiments search'

# Pick an experiment ID (e.g., 1), list its runs
doppler run --project claude-config --config dev -- bash -c \
  'export MLFLOW_TRACKING_URI="http://$MLFLOW_USERNAME:$MLFLOW_PASSWORD@$MLFLOW_HOST:$MLFLOW_PORT" && \
   uvx mlflow runs list --experiment-id 1' | head -20

# Pick a run ID, see its details
doppler run --project claude-config --config dev -- bash -c \
  'export MLFLOW_TRACKING_URI="http://$MLFLOW_USERNAME:$MLFLOW_PASSWORD@$MLFLOW_HOST:$MLFLOW_PORT" && \
   uvx mlflow runs describe --run-id <RUN_ID>'
```

---

## 🔐 Security & Credential Patterns

### Pattern 1: Doppler Atomic Secrets (Recommended)

**Why atomic secrets?**

- Rotation flexibility (change password without changing host)
- Audit trail per secret
- Multi-environment support (dev/staging/prod)

**Setup:**

```bash
# Store secrets atomically (zero-exposure)
echo 'mlflow.eonlabs.com' | doppler secrets set MLFLOW_HOST -p claude-config -c dev --silent
echo '5000' | doppler secrets set MLFLOW_PORT -p claude-config -c dev --silent
echo 'eonlabs' | doppler secrets set MLFLOW_USERNAME -p claude-config -c dev --silent
echo 'password' | doppler secrets set MLFLOW_PASSWORD -p claude-config -c dev --silent
```

**Usage (One-Liner):**

```bash
doppler run --project claude-config --config dev -- bash -c \
  'export MLFLOW_TRACKING_URI="http://$MLFLOW_USERNAME:$MLFLOW_PASSWORD@$MLFLOW_HOST:$MLFLOW_PORT" && \
   uvx mlflow <command>'
```

**Usage (Session-based):**

```bash
# Set environment for entire session
eval "$(doppler secrets download --project claude-config --config dev --format env-no-quotes --no-file | \
        grep -E '^(MLFLOW_HOST|MLFLOW_PORT|MLFLOW_USERNAME|MLFLOW_PASSWORD)=')"

export MLFLOW_TRACKING_URI="http://$MLFLOW_USERNAME:$MLFLOW_PASSWORD@$MLFLOW_HOST:$MLFLOW_PORT"

# Now run commands normally
uvx mlflow experiments search
uvx mlflow runs list --experiment-id 1
```

### Pattern 2: Environment Variable (Simple)

**For local/dev only:**

```bash
export MLFLOW_TRACKING_URI="http://localhost:5000"
uvx mlflow experiments search
```

**For remote with basic auth:**

```bash
export MLFLOW_TRACKING_URI="http://user:password@mlflow.example.com:5000"
uvx mlflow runs list --experiment-id 1
```

**⚠️ Security Warning**: Credentials visible in shell history and process list. Use Doppler for production.

---

## 🛠️ Troubleshooting Common Issues

### Issue 1: Connection Refused

**Error:**

```
ConnectionRefusedError: [Errno 61] Connection refused
```

**Diagnosis:**

1. Is MLflow server running?
   ```bash
   curl http://mlflow.example.com:5000/health
   ```
2. Is tracking URI correct?
   ```bash
   echo $MLFLOW_TRACKING_URI
   ```
3. Firewall blocking port?

**Fix:**

- Verify server is running: `mlflow server --host 0.0.0.0 --port 5000`
- Check network connectivity
- Verify credentials if using auth

### Issue 2: Authentication Failed

**Error:**

```
HTTPError: 401 Client Error: Unauthorized
```

**Diagnosis:**

1. Are credentials correct?
   ```bash
   doppler secrets --project claude-config --config dev | grep MLFLOW
   ```
2. Is URI formatted correctly?
   ```bash
   # Should be: http://USERNAME:PASSWORD@HOST:PORT
   echo $MLFLOW_TRACKING_URI
   ```

**Fix:**

- Update Doppler secrets if password changed
- Verify URI format includes credentials
- Test with curl:
  ```bash
  curl -u user:password http://mlflow.example.com:5000/api/2.0/mlflow/experiments/list
  ```

### Issue 3: Filter String Invalid

**Error:**

```
MlflowException: Invalid filter string
```

**Common mistakes:**

1. **Using OR** (not supported)
   - ❌ `"param = 'A' OR param = 'B'"`
   - ✅ Run two queries and merge

2. **Unquoted parameter values**
   - ❌ `"params.learning_rate = 0.001"` (number, but params are strings!)
   - ✅ `"params.learning_rate = '0.001'"` (quoted)

3. **Invalid operators**
   - ❌ `"metrics.accuracy BETWEEN 0.8 AND 0.9"`
   - ✅ `"metrics.accuracy > 0.8 AND metrics.accuracy < 0.9"`

**Fix:**

- Use AND-only filters
- Always quote parameter values
- Use valid operators: `=`, `!=`, `>`, `<`, `>=`, `<=`, `LIKE`, `ILIKE`

### Issue 4: No Results Found

**Issue:**

```bash
mlflow runs list --experiment-id 999
# Returns empty (no error)
```

**Diagnosis:**

1. Does experiment exist?
   ```bash
   mlflow experiments search | grep 999
   ```
2. Are there runs in this experiment?
   ```bash
   mlflow runs list --experiment-id 999 | wc -l
   ```

**Fix:**

- List all experiments: `mlflow experiments search`
- Verify experiment ID
- Check if runs exist with different status: `mlflow runs list --experiment-id 1 --view all`

### Issue 5: Doppler Secrets Not Loading

**Error:**

```
Error: unknown command "list" for "doppler projects"
```

**Diagnosis:**

1. Is Doppler CLI installed?
   ```bash
   doppler --version
   ```
2. Are you authenticated?
   ```bash
   doppler whoami
   ```

**Fix:**

- Install: `brew install dopplerhq/cli/doppler`
- Login: `doppler login`
- Verify project: `doppler projects`

---

## 📊 Capability Matrix (Quick Reference)

| Capability | Supported | Method | Constraints |
| --- | --- | --- | --- |
| **List experiments** | ✅ | `mlflow experiments search` | None |
| **List runs** | ✅ | `mlflow runs list` | Table output (parse or export CSV) |
| **Get run details** | ✅ | `mlflow runs describe` | JSON output, complete data |
| **Filter by metrics** | ✅ | Manual grep/awk | AND-only in Python API |
| **Filter by params** | ⚠️ | Manual grep/awk + quote values | AND-only, params are strings |
| **OR filters** | ❌ | Run multiple queries | MLflow limitation |
| **Export CSV** | ✅ | `mlflow experiments csv` | Efficient for bulk |
| **Metric history** | ❌ CLI / ✅ Python | Use Python API | CLI doesn't support time-series |
| **Aggregation** | ❌ | Client-side (awk/python) | No SUM/AVG in MLflow |
| **Create runs** | ❌ | Out of scope | Read-only skill |
| **Modify runs** | ❌ | Out of scope | Read-only skill |
| **Streaming** | ❌ | Pagination | Poll-based only |
| **Doppler creds** | ✅ | Atomic secrets pattern | Recommended for production |

---

## 🎓 Summary

**This skill helps you query MLflow within these boundaries:**

**✅ Can Do:**

- Find best models by metric
- Compare runs side-by-side
- Filter runs (AND-only)
- Export data (CSV/JSON)
- Detect overfitting
- List resources
- Use Doppler credentials securely

**❌ Cannot Do:**

- Create/modify/delete runs
- OR filters (workaround: multiple queries)
- Real-time streaming (workaround: pagination)
- Aggregation in queries (workaround: client-side)
- Parameter arithmetic (workaround: awk/python)

**Next Steps:**

1. Choose a workflow from "How Would You Like to Proceed?" section
2. Verify prerequisites
3. Follow guided steps
4. Ask questions if you encounter constraints

**Ready to proceed? Tell me:**

- Which workflow (A-G)?
- Or describe your custom query

I'll guide you through available options within the skill's boundaries.
