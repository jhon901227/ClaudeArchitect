---
description: Rules for CI configuration and shell scripts — loaded for .github/** and scripts/**
paths:
  - .github/**
  - scripts/**
  - "*.sh"
---

# CI & Scripts Rules

Applies when Claude edits GitHub Actions workflows or shell scripts.

## Shell Script Standards

- All scripts must start with `#!/usr/bin/env bash` and `set -euo pipefail`.
- Quote all variable expansions: `"$VAR"` not `$VAR`.
- Use `local` for function-scoped variables.
- Provide a usage comment at the top of each script.

## GitHub Actions Rules

- Pin action versions to a full SHA, not a tag: `uses: actions/checkout@11bd71901...` not `@v4`.
- Never hardcode secrets — use `${{ secrets.NAME }}` only.
- All jobs that deploy must have a `needs: [test, lint]` dependency.
- Separate lint, test, and build into distinct jobs for clear failure attribution.

## Forbidden

- `curl | bash` patterns — always download, verify checksum, then execute.
- Storing secrets in env vars in the workflow YAML (use GitHub Secrets).
- `continue-on-error: true` without a comment explaining the trade-off.