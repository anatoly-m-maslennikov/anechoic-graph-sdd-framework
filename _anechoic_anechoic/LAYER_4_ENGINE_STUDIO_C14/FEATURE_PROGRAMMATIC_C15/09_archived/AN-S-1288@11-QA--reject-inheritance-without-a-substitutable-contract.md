---
atom_family: SPEC
atom_id: AN-S-1288
container:
  component: C15
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 11
  updated_at: 2026-10-22 16:26:49 +0000
---
## Summary

Reject inheritance without a substitutable contract

# Reject inheritance without a substitutable contract

## Claim checked

one PROGRAMMATIC inheritance relationship exists **only** for a stable
substitutable subtype contract.

## Test case

evaluate one changed subclass that inherits behavior for code reuse but cannot
replace its base under the base contract.

## Acceptance criteria

pass **only** **when** the inheritance is rejected **and** the behavior is expressed by a
function, module, **or** composed collaborator.

## Failure disposition

reject the subtype boundary **until** substitutability is demonstrated **or**
inheritance is removed.

## Sources

- [CA-M-408 — Allocate owned state and lifecycle to objects](../05_method/CA-M-408-PROGRAMMATIC-STANDARD-IMPLEMENTATION_METHOD--allocate-owned-state-and-lifecycle-to-objects.md)
