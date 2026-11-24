---
atom_family: SPEC
atom_id: AN-S-1273
container:
  component: C15
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 25
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Surface one nonzero subprocess result

## Claim



### Prose Claim
#### Claim checked

one PROGRAMMATIC subprocess boundary observes **and** returns a non-zero exit
status with the context required for diagnosis **or** recovery.

#### Applicable conditions

apply **only** **when** a component invokes a subprocess. components **without** a
subprocess boundary are **not** applicable.

#### Test case

invoke one declared subprocess that returns a non-zero exit status.

#### Acceptance criteria

pass **only** **when** the boundary reports the explicit status **and** declared input
context **without** treating the invocation as successful.

#### Failure disposition

stop the affected operation **and** return the failure **to** its caller **or** recovery
owner.

#### Sources

- [CA-M-409 — Bound file and subprocess effects](../05_method/CA-M-409-PROGRAMMATIC-ENG_POLICY--bound-file-and-subprocess-effects.md)
