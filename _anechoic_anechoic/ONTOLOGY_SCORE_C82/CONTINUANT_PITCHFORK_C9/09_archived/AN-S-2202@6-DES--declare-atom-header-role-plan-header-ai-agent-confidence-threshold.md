---
atom_family: SPEC
atom_id: AN-S-2202
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 6
  updated_at: 2026-11-04 21:11:03 +0400
---
## Summary

Declare Atom/(.Header.Role := Plan).Header.AI Agent Confidence Threshold

## Claim

### Formal Claim

```CFEL
# model
Atom/(.Header.Role: Plan).Header.AI Agent Confidence Threshold:: [int, 0..100]{::0..1};

Atom/(.Header.Role: Plan).Header.AI Agent Confidence Threshold.*[]{::0};

# instances
Atom/(.Header.Role: Plan)//$plan;
Scope Unit/Project//$project{::1};

$plan.Header.AI Agent Confidence Threshold
  ?== LOOKUP(Relation//IS_CONTAINED_BY, Atom/(.Header.Role: Plan).Header.AI Agent Confidence Threshold)
  ?== $project.Settings.AI Agent Confidence Threshold
```
