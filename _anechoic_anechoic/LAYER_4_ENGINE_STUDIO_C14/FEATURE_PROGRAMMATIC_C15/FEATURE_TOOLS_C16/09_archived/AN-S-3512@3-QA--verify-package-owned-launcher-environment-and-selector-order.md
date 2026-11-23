---
atom_family: SPEC
atom_id: AN-S-3512
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 3
  updated_at: 2026-10-14 20:53:35 +0400
---
## Summary

Verify package-owned launcher, environment and selector order

# Summary

Verify package-owned launcher, environment and selector order

## Scope

the final target activation fixture.

## Claim

the QA case **must** prove that runtime command and environment resolve only package-owned bytes and the target selector is last, and **must not** allow checkout, env-file or partial-state activation.

## Details

The fixture verifies the distinct `.anechoic_install/current.toml` and target current selector, exact `uv run --locked --no-sync --no-env-file` argv, package-relative entrypoint, allowlisted environment and monotonic generation. It verifies that a package default creates `.anechoic_runtime/config.toml` only when absent and that existing config bytes survive first activation, upgrade, rollback and recovery. Failures inject checkout path, `--env-file`, missing lockfile, wrapper/Skill/projection failure, selector failure and an attempted config overwrite; previous activation or actual `recording_pending` selection remains authoritative.
