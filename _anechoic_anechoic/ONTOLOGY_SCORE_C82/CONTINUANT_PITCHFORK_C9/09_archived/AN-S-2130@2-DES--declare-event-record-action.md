---
atom_family: SPEC
atom_id: AN-S-2130
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

Declare Event Record.action

## Claim

### Formal Claim

```CFEL
# model
Event Record.action{::1}:: [string]{::1};

Event Record.action.*[]{::0};

Event Record.action: create;

Event Record.action: update;

Event Record.action: archive
```

