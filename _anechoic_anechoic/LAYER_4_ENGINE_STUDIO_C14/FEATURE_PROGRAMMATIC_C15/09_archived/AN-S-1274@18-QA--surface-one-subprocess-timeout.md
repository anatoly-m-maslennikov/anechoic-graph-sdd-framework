---
atom_family: SPEC
atom_id: AN-S-1274
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

Surface one subprocess timeout

# Surface one subprocess timeout

## Claim checked

one PROGRAMMATIC subprocess boundary observes **and** returns timeout completion
instead of waiting indefinitely **or** reporting a successful result.

## Applicable conditions

apply **only** **when** a component invokes a subprocess with a declared timeout.
components **without** a subprocess boundary are **not** applicable.

## Test case

invoke one declared subprocess that exceeds its declared timeout.

## Acceptance criteria

pass **only** **when** the boundary returns a typed timeout outcome with the declared
input context **and** no false success.

## Failure disposition

stop the affected operation **and** return timeout recovery **to** its owner.

## Sources

- [CA-M-409 — Bound file and subprocess effects](../05_method/CA-M-409-PROGRAMMATIC-ENG_POLICY--bound-file-and-subprocess-effects.md)
