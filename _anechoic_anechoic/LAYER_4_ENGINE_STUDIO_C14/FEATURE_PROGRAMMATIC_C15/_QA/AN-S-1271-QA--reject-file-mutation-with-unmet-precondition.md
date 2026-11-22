---
atom_family: SPEC
atom_id: AN-S-1271
container:
  component: C15
tier: 5
context:
  lens: QA
state:
  status: active
  version: 25
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Reject file mutation with unmet precondition

## Claim



### Prose Claim
#### Claim checked

one PROGRAMMATIC file mutation stops **before** writing, replacing, **or** removing a
file **when** its declared target **or** precondition is invalid.

#### Applicable conditions

apply **when** a component writes, replaces, **or** removes a file.

#### Test case

request one file mutation with a declared precondition that does **not** hold.

#### Acceptance criteria

pass **only** **when** the operation returns the precondition failure **and** leaves the
target bytes unchanged.

#### Failure disposition

reject the mutation **and** preserve the existing target for diagnosis.

#### Sources

- [CA-M-409 — Bound file and subprocess effects](../05_method/CA-M-409-PROGRAMMATIC-ENG_POLICY--bound-file-and-subprocess-effects.md)
