---
identity:
  atom_id: AN-S-1274
context:
  container:
    component: C15
  tier: 5
  lens: QA
state:
  status: active
  version: 25
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Surface one subprocess timeout

## Claim



### Prose Claim
#### Claim checked

one PROGRAMMATIC subprocess boundary observes **and** returns timeout completion
instead of waiting indefinitely **or** reporting a successful result.

#### Applicable conditions

apply **only** **when** a component invokes a subprocess with a declared timeout.
components **without** a subprocess boundary are **not** applicable.

#### Test case

invoke one declared subprocess that exceeds its declared timeout.

#### Acceptance criteria

pass **only** **when** the boundary returns a typed timeout outcome with the declared
input context **and** no false success.

#### Failure disposition

stop the affected operation **and** return timeout recovery **to** its owner.

#### Sources

- [CA-M-409 — Bound file and subprocess effects](../05_method/CA-M-409-PROGRAMMATIC-ENG_POLICY--bound-file-and-subprocess-effects.md)
