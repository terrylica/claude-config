# Repository Guidelines

## Project Structure & Module Organization

- `automation/` holds operational services: CNS lives in `automation/cns/` (Bash hooks and configs) and Lychee in `automation/lychee/` (runtime, setup, docs).
- `tools/` collects reusable Python and shell utilities such as `tools/workspace-cleanup.py` and shared helpers.
- `plugins/marketplaces/claude-code-plugins-plus/` maintains marketplace manifests, backup artifacts, and installer scripts.
- `docs/` is the canonical reference hub; file new material inside existing topic folders. Keep runtime artefacts in `system/`, `logs/`, and `media/` machine-neutral.

## Build, Test, and Development Commands

- `bash automation/cns/tests/unit/test_config_loader.sh` — CNS unit tests via the shared harness.
- `bash automation/cns/tests/integration/test_foundation_integration.sh` — end-to-end CNS hook validation.
- `uv run --active python automation/lychee/testing/test-notification-emit.py` — simulate Telegram notifications.
- `uv run --active python tools/workspace-cleanup.py --dry-run` — confirm workspace utilities without side effects.
- `bash plugins/marketplaces/claude-code-plugins-plus/scripts/test-plugin-installation.sh` — sanity-check marketplace packaging.

## Coding Style & Naming Conventions

- Bash uses `#!/bin/bash`, prefer `set -euo pipefail`, `[[ … ]]` tests, 4-space indents, and `snake_case` functions (`automation/cns/conversation_handler.sh` is the baseline).
- Python follows PEP 8, keeps modules importable, runs via `uv run --active python …`, and orders imports stdlib → third-party → local.
- Configs in `automation/*/config/` and `docs/` keep 2-space JSON/YAML indentation, placeholders for secrets, and trailing newlines.

## Testing Guidelines

- Place new shell suites under `automation/<component>/tests/{unit,integration}/` and source `automation/cns/lib/testing/test_runner.sh`.
- Python checks sit beside their subsystem (`automation/lychee/testing/`, `tools/doc-intelligence/`) and use `test_<feature>.py` naming.
- Capture deterministic assertions or log snippets; paste command outputs in PRs.
- For launch agents, Zellij configs, or stateful hooks, add a dry-run mode so reviewers can replay safely.

## Commit & Pull Request Guidelines

- Use Conventional Commits (`type(scope): summary`) as in `fix(telegram): …`; match the scope to the touched directory.
- Keep commits atomic with code, tests, and docs together; avoid unrelated formatting sweeps.
- PRs need a concise summary, linked issue/spec, commands executed, and evidence (logs or screenshots) for user-facing automation.
- Update `docs/` or subsystem READMEs when behavior or configuration shifts; mention migration steps if state layout changes.

## Security & Configuration Tips

- Keep real credentials out of git; ship placeholders in `automation/*/config/*.json` and document overrides in `docs/setup/`.
- Scrub workspace paths from logs before sharing; `automation/lychee/state/` and `logs/` often expose session IDs.
- Stage agent definitions in `agents-disabled/` until production ready and cross-reference them in `docs/agents/`.
