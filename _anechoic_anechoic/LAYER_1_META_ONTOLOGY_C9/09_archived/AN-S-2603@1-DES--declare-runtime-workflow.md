---
atom_family: SPEC
atom_id: AN-S-2603
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-04 00:31:19 +0400
---

## Summary

Declare Runtime Workflow

## Claim

### Formal Claim

```CFEL
Atom/(.Header.Role := Operations)/Workflow/(.Purpose := Runtime)
```

## Semantics

A Runtime Workflow is a Workflow whose Purpose is Runtime: it provides behavior through a Project's delivered result during its operation. In ANECHOIC, examples include Create Draft, Promote Draft and Archive Atom.

It inherits Workflow's shared Step, Substep and Action model. Purpose describes use relative to a Project and does not change the canonical definition's owning Scope Unit.
