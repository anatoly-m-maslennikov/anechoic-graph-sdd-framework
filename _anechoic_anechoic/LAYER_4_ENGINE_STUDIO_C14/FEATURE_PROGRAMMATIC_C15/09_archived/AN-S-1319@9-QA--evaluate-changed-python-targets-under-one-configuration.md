---
atom_family: SPEC
atom_id: AN-S-1319
container:
  component: C15
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 9
  updated_at: 2026-10-23 03:17:34 +0400
---
## Summary

Evaluate changed Python targets under one configuration

# Evaluate changed Python targets under one configuration

## Claim checked

**every** changed Python target receives distinct syntax, Ruff, Mypy, **and** relevant
behavioral evidence under one declared interpreter **and** configuration.

## Test case

evaluate one changed target for which Ruff passes, Mypy fails, **and** its focused
behavioral case passes.

## Acceptance criteria

pass **only** **when** the three results remain separate **and** the aggregate changed-code
gate fails with the target, diagnostic, boundary, **and** replay command.

## Failure disposition

reject masking one mechanism with another **and** return the failed evidence **to** its
owner.

## Sources

- [Ruff documentation](https://docs.astral.sh/ruff/)
- [Mypy documentation](https://mypy.readthedocs.io/en/stable/)
- [CA-M-164 — Ratchet typing and automation adoption](../05_method/CA-M-164-PROGRAMMATIC-CORE-METHOD--ratchet-typing-and-automation-adoption.md)
