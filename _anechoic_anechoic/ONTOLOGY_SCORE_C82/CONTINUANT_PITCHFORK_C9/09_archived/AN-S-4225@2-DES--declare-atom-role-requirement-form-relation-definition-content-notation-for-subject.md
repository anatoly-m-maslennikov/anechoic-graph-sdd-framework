---
atom_family: SPEC
atom_id: AN-S-4225
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Declare Atom/(.Role := Requirement)/(.Form := Relation Definition).Content.notation_for_subject

## Claim

When a short subject notation is admitted for the Relation, this Property is required.

```CFEL
Atom/(.Role: Requirement)/(.Form: Relation Definition).Content.notation_for_subject{:0..1}: [string]{:1};
Atom/(.Role: Requirement)/(.Form: Relation Definition).Content.notation_for_subject.*[]{:0}
```
