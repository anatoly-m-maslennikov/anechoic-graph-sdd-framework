---
atom_family: SPEC
atom_id: AN-S-1276
container:
  component: C15
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 15
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Verify structured diagnostic schema

# Verify structured diagnostic schema

## Claim checked

one PROGRAMMATIC operational diagnostic uses an admitted severity **and** provides
the actionable contextual fields required by its declared schema.

## Applicable conditions

apply **when** a component emits a diagnostic for normal operation, degraded
operation, failure, recovery, **or** diagnostic detail.

## Test case

evaluate one emitted diagnostic record for a declared component event.

## Acceptance criteria

pass **only** **when** the record uses ERROR, WARNING, INFO, **or** DEBUG, includes its
declared actionable contextual fields, **and** does **not** repurpose Journal history
as an operational diagnostic.

## Failure disposition

reject the diagnostic path **until** its schema **and** severity are corrected.

## Sources

- [CA-M-414 — Emit structured operational diagnostics](../05_method/CA-M-414-PROGRAMMATIC-STANDARD-ENG_POLICY--emit-structured-operational-diagnostics.md)
