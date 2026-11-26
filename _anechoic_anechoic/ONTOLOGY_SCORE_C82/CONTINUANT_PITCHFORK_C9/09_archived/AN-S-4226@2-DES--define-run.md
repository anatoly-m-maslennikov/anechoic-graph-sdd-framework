---
atom_family: SPEC
atom_id: AN-S-4226
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

Define RUN

## Claim

RUN binds a Step or Substep to an Action for execution.

```CFEL
(in (Step, Substep))// ((RUN)) Action//;
Action// ((IS_RUN_BY)) (in (Step, Substep))//;
RUN ((HAS_INVERSE)) IS_RUN_BY
```
