---
atom_family: SPEC
atom_id: AN-S-4319
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-07 15:18:44 +0400
---

## Summary

Declare Decision Form

## Claim

### Formal Claim

```CFEL
# model
Atom/(.Header.Form := Decision);

# instances
Atom/(.Header.Form := Decision)//$decision.Header.Role:: [in (Method, Evaluation, Delivery, Operations)]{::1}
```

## Semantics

A Decision records a particular local choice. Applicable governing constraints continue to apply.
