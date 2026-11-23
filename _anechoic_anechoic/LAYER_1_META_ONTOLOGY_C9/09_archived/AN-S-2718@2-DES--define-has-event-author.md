---
atom_family: SPEC
atom_id: AN-S-2718
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

Define HAS_EVENT_AUTHOR

## Claim

HAS_EVENT_AUTHOR identifies the Actor who performed the recorded event.

```CFEL
Event Record// ((HAS_EVENT_AUTHOR)) Actor//;
HAS_EVENT_AUTHOR ((HAS_INVERSE)) IS_EVENT_AUTHOR_OF
```
