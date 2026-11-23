---
atom_family: SPEC
atom_id: AN-S-1315
container:
  component: C15
tier: 1
context:
  lens: QA
state:
  status: archived
  version: 17
  updated_at: 2026-10-26 00:46:35 +0400
---
## Summary

Verify machine-contract compatibility

# Verify machine-contract compatibility

## Claim checked

one public machine boundary preserves structural, semantic, version, **and**
adjacent producer-consumer compatibility.

## Test case

pass valid, missing-field, forbidden-field, wrong-type, **and** unsupported-version
fixtures from one producer **to** its supported adjacent consumer.

## Acceptance criteria

pass **only** **when** valid meaning survives, structural **and** semantic failures remain
distinct, unsupported versions are rejected, **and** the declared compatibility
promise is preserved **or** explicitly replaced.

## Failure disposition

reject release **or** the compatibility claim **until** the boundary is restored.

## Sources

- [JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12)
- [CA-M-166 — Preserve declared interface compatibility boundaries](../05_method/CA-M-166-PROGRAMMATIC-CORE-METHOD--preserve-declared-interface-compatibility-boundaries.md)
