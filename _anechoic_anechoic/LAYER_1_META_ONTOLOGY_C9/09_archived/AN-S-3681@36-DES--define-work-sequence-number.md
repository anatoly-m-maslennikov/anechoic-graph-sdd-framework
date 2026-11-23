---
atom_family: SPEC
atom_id: AN-S-3681
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 36
  updated_at: 2026-10-29 10:13:50 +0400
---
## Summary

Define Work Sequence Number

## Claim scope

Work Sequence Numbers for Plans directly contained by one Plan or sharing one top-level Plan container.

## Claim

The optional explicit ordinal does not determine execution order; when supplied, its existing positive and local-uniqueness rules remain applicable.

a Work Sequence Number **means** a mutable ordinal navigation value for a Plan among Plans directly contained by the same Plan **or** sharing a top-level Plan container; it does **not** establish execution order.

### Formal claim

```text
Entity/Object/Continuant/Governing Objects/Atom/Content Role: Plan.Work Sequence Number[int]{0..1}
```
