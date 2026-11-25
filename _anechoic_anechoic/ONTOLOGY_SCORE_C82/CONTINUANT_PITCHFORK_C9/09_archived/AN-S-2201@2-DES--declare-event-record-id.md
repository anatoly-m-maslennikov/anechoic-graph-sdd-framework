---
atom_family: SPEC
atom_id: AN-S-2201
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

Declare Event Record.ID

## Claim

### Formal Claim

```CFEL
# model
Event Record.ID{::1}:: [string]{::1};

Event Record.ID.*[]{::0};

# instances
UNIQUE(Event Record//$event_record, (.ID))
```

