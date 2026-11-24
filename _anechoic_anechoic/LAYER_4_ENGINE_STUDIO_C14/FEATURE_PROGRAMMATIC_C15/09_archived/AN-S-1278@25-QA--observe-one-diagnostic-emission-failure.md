---
atom_family: SPEC
atom_id: AN-S-1278
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

Observe one diagnostic emission failure

## Claim



### Prose Claim
#### Claim checked

one failure **to** emit a PROGRAMMATIC operational diagnostic is observable **and**
does **not** silently break the primary work.

#### Applicable conditions

apply **when** a component has a declared operational-diagnostic path **and** a
separate primary work outcome.

#### Test case

cause one declared diagnostic emission **to** fail while the associated primary
work remains **otherwise** executable.

#### Acceptance criteria

pass **only** **when** the primary work reaches its declared outcome **or** failure
boundary, **and** the diagnostic-emission failure is itself observable through its
declared recovery **or** reporting path.

#### Failure disposition

reject the diagnostic path **when** it hides its own failure **or** silently changes
the primary work result.

#### Sources

- [CA-M-414 — Emit structured operational diagnostics](../05_method/CA-M-414-PROGRAMMATIC-ENG_POLICY--emit-structured-operational-diagnostics.md)
