---
atom_family: SPEC
atom_id: AN-S-1511
container:
  component: C15
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 13
  updated_at: 2026-10-23 23:58:37 +0400
---
## Summary

Reject unbounded production DEBUG logging

# Reject unbounded production DEBUG logging

## Claim checked

production DEBUG logging is disabled by default **and** **may** be enabled **only** through
a bounded selector with automatic expiry **and** unchanged redaction.

## Test case

evaluate one production component configuration that enables DEBUG globally
**without** an expiry.

## Acceptance criteria

pass **only** **when** the configuration is rejected **before** deployment.

## Failure disposition

block production DEBUG **until** component, subject, run, entity, **or** equivalent
scope **and** automatic expiry are present.

## Sources

- [CA-M-414 — Emit structured operational diagnostics](../05_method/CA-M-414-PROGRAMMATIC-STANDARD-ENG_POLICY--emit-structured-operational-diagnostics.md)
