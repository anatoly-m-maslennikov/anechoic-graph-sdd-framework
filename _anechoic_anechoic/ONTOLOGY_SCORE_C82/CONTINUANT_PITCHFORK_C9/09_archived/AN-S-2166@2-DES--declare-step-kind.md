---
atom_family: SPEC
atom_id: AN-S-2166
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

Declare Step.Kind

## Claim

### Prose Claim

A Step has exactly one Kind: Input, Execution, or Decision. Kind classifies the Step in the Workflow and is independent of its Agentic Step Execution Context.

### Formal Claim

```CFEL
# model
Step.Kind ((IS_PROPERTY_OF)) Step;
```
