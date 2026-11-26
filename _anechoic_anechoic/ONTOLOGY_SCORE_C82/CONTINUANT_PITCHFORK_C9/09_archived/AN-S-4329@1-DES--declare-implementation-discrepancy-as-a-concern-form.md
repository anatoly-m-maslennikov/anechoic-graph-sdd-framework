---
atom_family: SPEC
atom_id: AN-S-4329
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: '2026-11-12T14:56:23.632240+00:00'
---
## Summary

Declare Implementation Discrepancy as a Concern Form

## Claim

### Prose Claim

Identify the applicable RMEDO Atom and the code location. State what the Atom specifies and what the code does.

Resolved means the code and applicable specification agree. Canceled means the recorded comparison is obsolete because the code or specification changed scope or was retired.

### Formal Claim

```CFEL
# model
Atom/(.Header.Context.Role in (Concern)).Header.Context.Form :: Implementation Discrepancy;
```

## Semantics

An Implementation Discrepancy records a mismatch between the code and an applicable RMEDO Atom.
