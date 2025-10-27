---
name: doppler-workflows
description: Complete credential management using Doppler CLI for PyPI tokens and AWS keys. Use when publishing Python packages, rotating AWS credentials, managing project-scoped tokens, troubleshooting authentication errors, or setting up multi-service credential strategies with Doppler.
allowed-tools: Read, Bash
---

# Doppler Credential Workflows Skill

## Quick Reference

**When to use this skill:**

- Publishing Python packages to PyPI
- Rotating AWS access keys
- Managing credentials across multiple services
- Troubleshooting authentication failures (403, InvalidClientTokenId)
- Setting up Doppler credential injection patterns
- Multi-token/multi-account strategies

## Core Pattern: Doppler CLI

**Standard Usage:**

```bash
doppler run --project <project> --config <config> --command='<command>'
```

**Why --command flag:**

- Official Doppler pattern (auto-detects shell)
- Ensures variables expand AFTER Doppler injects them
- Without it: shell expands `$VAR` before Doppler runs → empty string

---

## Use Case 1: PyPI Package Publishing

### Quick Start

```bash
# Publish package
doppler run --project claude-config --config dev \
  --command='uv publish --token "$PYPI_TOKEN"'
```

### Token Setup

**Doppler Storage:**

- Project: `claude-config`
- Config: `dev`
- Secret naming: `PYPI_TOKEN` (primary), `PYPI_TOKEN_{ABBREV}` (additional packages)

**Active Tokens:**

- `PYPI_TOKEN` → atr-adaptive-laguerre (aal token)
- `PYPI_TOKEN_GCD` → gapless-crypto-data (gcd token)

**Create New Token:**

```bash
# Step 1: Create project-scoped token on PyPI
# Go to: https://pypi.org/manage/account/token/
# Select specific project (NOT account-wide)

# Step 2: Store in Doppler (use stdin to avoid escaping)
echo -n 'pypi-AgEI...' | doppler secrets set PYPI_TOKEN_XXX \
  --project claude-config --config dev

# Step 3: Verify injection
doppler run --project claude-config --config dev \
  --command='echo "Length: ${#PYPI_TOKEN_XXX}"'
# Should show: 220-224 (valid token length)

# Step 4: Test publish
doppler run --project claude-config --config dev \
  --command='uv publish --token "$PYPI_TOKEN_XXX"'
```

### PyPI Troubleshooting

**Issue: 403 Forbidden**

- Root cause: Token expired/revoked on PyPI
- Solution: Create new project-scoped token, update Doppler
- Verify: `doppler secrets get PYPI_TOKEN --plain | head -c 50` (should start with `pypi-AgEI`)

**Issue: Empty Token (Variable Not Expanding)**

- Root cause: Not using `--command` flag
- ❌ Wrong: `doppler run -- uv publish --token "$VAR"`
- ✅ Correct: `doppler run --command='uv publish --token "$VAR"'`

**Issue: Display vs Actual Value**

- `doppler secrets get` adds newline to display (formatting only)
- Actual value has NO newline when injected
- Verify: `doppler run --command='printf "%s" "$TOKEN" | wc -c'`

---

## Use Case 2: AWS Credential Management

### Quick Start

```bash
# Use AWS credentials
doppler run --project aws-credentials --config dev \
  --command='aws s3 ls --region $AWS_DEFAULT_REGION'
```

### Credential Setup

**Doppler Storage:**

- Project: `aws-credentials`
- Configs: `dev`, `staging`, `prod` (one per AWS account)

**Required Secrets:**

```
AWS_ACCESS_KEY_ID           # IAM access key (20 chars)
AWS_SECRET_ACCESS_KEY       # IAM secret (40 chars)
AWS_DEFAULT_REGION          # e.g., us-east-1
AWS_ACCOUNT_ID              # For audit trail
AWS_LAST_ROTATED_DATE       # Timestamp
AWS_ROTATION_INTERVAL_DAYS  # e.g., 90
```

### AWS Rotation Workflow

**Step 1: Create New Credentials**

```bash
# In AWS IAM Console:
# Users → Select user → Security credentials → Create access key
```

**Step 2: Store in Doppler**

```bash
echo -n 'AKIAIOSFODNN7EXAMPLE' | doppler secrets set AWS_ACCESS_KEY_ID \
  --project aws-credentials --config dev

echo -n 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY' | \
  doppler secrets set AWS_SECRET_ACCESS_KEY \
  --project aws-credentials --config dev

doppler secrets set AWS_LAST_ROTATED_DATE \
  --project aws-credentials --config dev \
  --value "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
```

**Step 3: Verify Injection**

```bash
doppler run --project aws-credentials --config dev \
  --command='echo "KEY: ${#AWS_ACCESS_KEY_ID}; SECRET: ${#AWS_SECRET_ACCESS_KEY}"'
# Expected: KEY: 20; SECRET: 40
```

**Step 4: Test AWS Access**

```bash
doppler run --project aws-credentials --config dev \
  --command='aws sts get-caller-identity'
# Should show your UserId, Account, Arn
```

**Step 5: Deactivate Old Key**

```bash
# In AWS IAM Console:
# Mark old key as Inactive → Wait 24 hours → Delete
```

### AWS Troubleshooting

**Issue: 403 Forbidden / InvalidClientTokenId**

- Root cause: Credentials expired/rotated elsewhere, or wrong region
- Verify: `doppler run --command='aws sts get-caller-identity'`
- Check region: `doppler secrets get AWS_DEFAULT_REGION --plain`

**Issue: Works on One Machine, Not Another**

- Root cause: Different Doppler config or HOME variable
- Verify: `doppler me` (check logged-in user), `echo $HOME`

---

## Multi-Service / Multi-Account Patterns

### Multiple PyPI Packages

```bash
# Package 1
doppler run --project claude-config --config dev \
  --command='uv publish --token "$PYPI_TOKEN"'

# Package 2
doppler run --project claude-config --config dev \
  --command='uv publish --token "$PYPI_TOKEN_GCD"'
```

### Multiple AWS Accounts

```bash
# Deploy to staging
doppler run --project aws-credentials --config staging \
  --command='aws s3 sync dist/ s3://staging-bucket/'

# Deploy to production
doppler run --project aws-credentials --config prod \
  --command='aws s3 sync dist/ s3://prod-bucket/'
```

---

## Best Practices

1. **Always use --command flag** for credential injection
2. **Use project-scoped tokens** (PyPI) for better security
3. **Rotate credentials regularly** (90 days recommended)
4. **Document with Doppler notes**: `doppler secrets notes set <SECRET> "<note>" --project <project>`
5. **Use stdin for storing secrets**: `echo -n 'secret' | doppler secrets set`
6. **Test injection before using**: `echo ${#VAR}` to verify length
7. **Multi-token naming**: `SERVICE_TOKEN_{ABBREV}` for clarity

---

## Setup Checklist

**PyPI:**

- [ ] Create project-scoped token on PyPI
- [ ] Store in `claude-config/dev/PYPI_TOKEN`
- [ ] Verify injection: `doppler run --command='echo ${#PYPI_TOKEN}'`
- [ ] Test publish with `--verbose` flag first

**AWS:**

- [ ] Create IAM access key
- [ ] Store in `aws-credentials/{env}/AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`
- [ ] Verify injection: `doppler run --command='echo ${#AWS_ACCESS_KEY_ID}'`
- [ ] Test with `aws sts get-caller-identity`
- [ ] Set rotation reminder (90 days)

---

## See Also

- **PyPI Reference**: Check `PYPI_REFERENCE.yaml` for complete PyPI spec with all workflows
- **AWS Reference**: Check `AWS_SPECIFICATION.yaml` for complete AWS credential architecture
- **AWS Workflow**: Check `AWS_WORKFLOW.md` for detailed step-by-step setup
- **General Doppler**: `specifications/doppler-integration.yaml` for CLI patterns
