---
atom_family: SPEC
atom_id: AN-S-2169
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

Declare Step.Outputs

## Claim

### Prose Claim

A Step declares its outputs when it produces values for subsequent Steps or the enclosing Workflow. A previous Step output is one permitted source of a binding.

### Formal Claim

```CFEL
# model
Step.Outputs ((IS_PROPERTY_OF)) Step;
```
