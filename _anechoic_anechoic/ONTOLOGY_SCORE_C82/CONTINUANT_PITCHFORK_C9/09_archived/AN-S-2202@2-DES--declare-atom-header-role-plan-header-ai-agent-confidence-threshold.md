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
  version: 2
  updated_at: 2026-11-04 05:21:15 +0400
---
## Summary

Declare Atom/(.Header.Role := Plan).Header.AI Agent Confidence Threshold

## Claim

### Formal Claim

```CFEL
# model
Atom/(.Header.Role: Plan).Header.AI Agent Confidence Threshold: [int]{:0..1};

Atom/(.Header.Role: Plan).Header.AI Agent Confidence Threshold.*[]{:0};

# instances
Atom/(.Header.Role: Plan).Header.AI Agent Confidence Threshold
  ?= LOOKUP(Relation//IS_CONTAINED_BY, Atom/(.Header.Role: Plan).Header.AI Agent Confidence Threshold)
  ?= Scope Unit/Project//$project.Settings.AI Agent Confidence Threshold
```
