---
atom_family: SPEC
atom_id: AN-S-2168
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-11 16:04:42 +0400
---

## Summary

Declare Step.Fixed Parameters

## Claim

### Prose Claim

A Step may declare fixed parameter values for its invocation. A fixed value is one permitted source of a binding.

### Formal Claim

```CFEL
# model
Step.Fixed Parameters ((IS_PROPERTY_OF)) Step;
```
