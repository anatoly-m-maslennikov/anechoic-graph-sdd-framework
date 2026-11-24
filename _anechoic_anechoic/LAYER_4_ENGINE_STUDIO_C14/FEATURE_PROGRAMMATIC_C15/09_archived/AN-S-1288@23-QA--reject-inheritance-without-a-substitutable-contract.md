---
atom_family: SPEC
atom_id: AN-S-1288
container:
  component: C15
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 23
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Reject inheritance without a substitutable contract

## Claim



### Prose Claim
#### Claim checked

one PROGRAMMATIC inheritance relationship exists **only** for a stable
substitutable subtype contract.

#### Test case

evaluate one changed subclass that inherits behavior for code reuse but cannot
replace its base under the base contract.

#### Acceptance criteria

pass **only** **when** the inheritance is rejected **and** the behavior is expressed by a
function, module, **or** composed collaborator.

#### Failure disposition

reject the subtype boundary **until** substitutability is demonstrated **or**
inheritance is removed.

#### Sources

- [CA-M-408 — Allocate owned state and lifecycle to objects](../05_method/CA-M-408-PROGRAMMATIC-ENG_POLICY--allocate-owned-state-and-lifecycle-to-objects.md)
