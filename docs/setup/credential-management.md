# Credential Management & Security

**Primary Method**: Doppler CLI for zero-config credential injection

**Specification**: [`specifications/doppler-integration.yaml`](../../specifications/doppler-integration.yaml)

---

## Doppler Projects

### claude-config

**Configs**: `dev`, `dev_personal`, `stg`, `prd`

**Credentials**:

- `PUSHOVER_TOKEN`, `PUSHOVER_USER` - Pushover notification credentials
- `PYPI_TOKEN` - PyPI publishing token (entire account scope)
- `ATUIN_USERNAME`, `ATUIN_EMAIL`, `ATUIN_KEY` - Atuin shell history sync credentials
- `NOTION_API_TOKEN` - Notion internal integration token (Touchstone Docs Reader)
- `NOTION_TOUCHSTONE_PAGE_ID` - Touchstone Service Operator Manual page ID
- `EONLABS_ADMIN_USERNAME`, `EONLABS_ADMIN_PASSWORD` - EonLabs Admin UI login (Touchstone, Model Performance)

**Usage Examples**:

```bash
# PyPI Publishing
doppler run --project claude-config --config dev -- uv publish --token "$PYPI_TOKEN"

# Notion API access
doppler run --project claude-config --config dev -- python3 util/touchstone/fetch_notion_docs.py

# With Pushover notifications
doppler run --project claude-config --config dev -- your-command
```

**Adding Documentation to Secrets**:

```bash
# Add or update secret notes via CLI
doppler secrets notes set <SECRET_NAME> "<note>" --project claude-config

# Example
doppler secrets notes set NOTION_API_TOKEN "Notion Internal Integration Secret | Purpose: Fetch Touchstone docs" --project claude-config
```

---

### aws-credentials

**Config**: `dev`

**Specifications**:

- [`specifications/aws-credentials-management.yaml`](../../specifications/aws-credentials-management.yaml)
- [`docs/setup/aws-credentials-doppler.md`](aws-credentials-doppler.md) - Rotation and usage workflows
- [`docs/setup/aws-credentials-elimination.md`](aws-credentials-elimination.md) - Reference implementation for ml-feature-experiments

**Account Details**:

- Account: `050214414362` (EonLabs)
- IAM User: `terryli`
- Region: `us-west-2`

**Features**:

- Zero-exposure rotation
- Dual-key testing
- Read-only audits
- Comprehensive documentation

**Usage**:

```bash
doppler run --project aws-credentials --config dev -- aws <command>
```

---

## Usage Pattern

```bash
doppler run --project <project> --config <config> -- <command>
```

**Available Projects**:

- `claude-config` - Pushover, PyPI, Atuin credentials
- `aws-credentials` - AWS IAM credentials for EonLabs account
