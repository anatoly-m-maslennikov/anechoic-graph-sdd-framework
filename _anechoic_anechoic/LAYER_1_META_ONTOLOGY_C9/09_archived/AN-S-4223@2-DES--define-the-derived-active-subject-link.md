---
atom_family: SPEC
atom_id: AN-S-4223
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

Define the derived active Subject link

## Claim

HAS_ACTIVE_SUBJECT links an Atom to the thing or topic named by its active Subject. Derive it from subjects.active. A Declaration addresses a Node; other Atoms are not restricted to the Node branch.

```CFEL
Atom/(.Role: Requirement)/(.Form: Declaration)// ((HAS_ACTIVE_SUBJECT)) (Node, Node/**, .**)
```
