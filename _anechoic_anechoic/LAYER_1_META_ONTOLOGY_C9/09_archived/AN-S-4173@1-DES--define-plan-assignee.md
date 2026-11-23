---
atom_family: SPEC
atom_id: AN-S-4173
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-29 17:09:47 +0400
---
## Summary

Define Plan Assignee

## Claim

Plan.Assignee means an optional local assignee override for Plan work; when it is absent, the applicable inherited or default assignment remains in force.

### Formal claim

```text
Entity/Object/Continuant/Governing Objects/Atom/Content Role: Plan.Assignee[string]{0..1}
```

## Details

Source meaning: CA-R-1338, CA-R-1584, CA-R-1585, CA-D-473. Scope-specific constraints remain in their governing Rs.
