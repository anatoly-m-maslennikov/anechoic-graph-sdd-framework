---
atom_family: SPEC
atom_id: AN-S-1262
container:
  component: C15
tier: 4
context:
  lens: QA
state:
  status: active
  version: 27
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Verify changed component technical-contract conformance

## Claim



### Prose Claim
#### Claim checked

one changed PROGRAMMATIC Tool, App backend service, **or** MCP component conforms
**to** the Python, runtime, **and** dependency selections owned by accepted Methods,
as materialized **in** current configuration **and** Implementation.

#### Applicable conditions

apply **when** such a component is added **or** materially changed **and** no bounded
technical-contract exception is proposed.

#### Test case

evaluate one changed component against the applicable Method-owned selections
**and** compare its configuration **and** Implementation carriers with those
selections.

#### Acceptance criteria

pass **only** **when** the component conforms **to** **every** applicable Method-owned
selection, its materializations agree, **and** no configuration, Implementation,
**or** Delivery carrier claims independent selection authority.

#### Failure disposition

reject admission **or** release of the component **until** it conforms **or** enters the
separate bounded-exception evaluation.

#### Sources

- [CA-M-415 — Implement PROGRAMMATIC components in Python](../05_method/CA-M-415-PROGRAMMATIC-ENG_POLICY--implement-programmatic-components-in-python.md)
