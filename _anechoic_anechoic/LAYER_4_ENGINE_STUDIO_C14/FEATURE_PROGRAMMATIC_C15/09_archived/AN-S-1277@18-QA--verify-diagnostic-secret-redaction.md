---
atom_family: SPEC
atom_id: AN-S-1277
container:
  component: C15
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 18
  updated_at: 2026-10-24 10:48:25 +0400
---
## Summary

Verify diagnostic secret redaction

# Verify diagnostic secret redaction

## Claim checked

one PROGRAMMATIC diagnostic path sanitizes a sensitive input **before** its record
is exposed **to** the declared sink.

## Applicable conditions

apply **when** a diagnostic path could receive sensitive **or** secret-bearing input.
paths whose declared inputs contain no such value are **not** applicable.

## Test case

Supply one secret-bearing input **to** one declared diagnostic path.

## Acceptance criteria

pass **only** **when** the exposed record retains the diagnostic context while omitting
**or** irreversibly redacting the secret-bearing value.

## Failure disposition

stop the diagnostic path **and** correct its sanitization boundary **before** release.

## Sources

- [CA-M-414 — Emit structured operational diagnostics](../05_method/CA-M-414-PROGRAMMATIC-ENG_POLICY--emit-structured-operational-diagnostics.md)
