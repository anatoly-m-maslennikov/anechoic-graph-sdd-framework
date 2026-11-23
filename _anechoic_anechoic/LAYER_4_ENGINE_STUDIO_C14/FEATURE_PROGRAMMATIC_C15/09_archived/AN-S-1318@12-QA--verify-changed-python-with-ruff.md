---
atom_family: SPEC
atom_id: AN-S-1318
container:
  component: C15
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 12
  updated_at: 2026-10-22 16:26:49 +0000
---
## Summary

Verify changed Python with Ruff

# Verify changed Python with Ruff

## Claim checked

changed Python passes the one admitted Ruff format, lint, **and** complexity
profile **or** carries one bounded exception.

## Test case

run the pinned Ruff profile against one changed module containing an executable
unit above the configured `C901` maximum.

## Acceptance criteria

pass **only** **when** **all** of the following hold:

- Ruff reports the unit that exceeds the configured maximum.
- the change is rejected **or** an accepted bounded exception records the rule, value, reason, **and** review condition.

## Failure disposition

reject the changed target **until** the diagnostic is resolved **or** bounded.

## Sources

- [Ruff: complex-structure rule](https://docs.astral.sh/ruff/rules/complex-structure/)
- [CA-M-428 — Use Ruff for Python formatting, linting, and complexity](../05_method/CA-M-428-PROGRAMMATIC-STANDARD-IMPLEMENTATION_DECISION--use-ruff-for-python-formatting-linting-and-complexity.md)
