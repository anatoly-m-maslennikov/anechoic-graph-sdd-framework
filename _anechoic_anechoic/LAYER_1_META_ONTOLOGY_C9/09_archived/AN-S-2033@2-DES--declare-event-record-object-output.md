---
atom_family: SPEC
atom_id: AN-S-2033
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

Declare Event Record.object_output

## Claim

### Formal Claim

```CFEL
# model
Event Record.object_output{::0..1}:: []{::0};

Event Record.object_output.*[in(id,version,updated_at)]{::2..3}
```

