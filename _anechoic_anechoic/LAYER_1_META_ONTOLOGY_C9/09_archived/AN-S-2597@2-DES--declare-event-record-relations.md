---
atom_family: SPEC
atom_id: AN-S-2597
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

Declare Event Record.Relations

## Claim

### Formal Claim

```CFEL
# model
Event Record.Relations{::1}:: []{::0};

# instances
Event Record.Relations.*[Relation//$relation]{::0+}
```

