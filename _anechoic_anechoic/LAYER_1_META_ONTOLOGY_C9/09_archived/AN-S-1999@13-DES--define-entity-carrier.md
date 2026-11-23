---
atom_family: SPEC
atom_id: AN-S-1999
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 13
  updated_at: 2026-10-29 09:34:45 +0400
---
## Summary

Define Entity/Carrier

## Claim scope

Carrier representations of Continuants.

## Claim

A Carrier **means** a storage representation of a Continuant, distinct from what it represents. A Carrier can represent a record of an Occurrent, **not** the Occurrent itself.

### Formal claim

```text
Carrier.ID[string]{1}
Carrier.Canonical Address[string]{1}
Carrier.Format[string]{1}
```

For implementation_of, the direct owner is the governed Implementation Carrier and each tuple targets the specification Atom it implements. For evidence_for, the direct owner is the evidence Carrier and each tuple targets the Evaluation or Implementation Carrier it supports. These are endpoint permissions, not extra fields on reusable Relation Types or additional storage facts for their derived inverses.

