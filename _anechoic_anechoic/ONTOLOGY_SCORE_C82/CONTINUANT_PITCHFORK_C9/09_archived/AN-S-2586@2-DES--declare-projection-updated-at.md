---
atom_family: SPEC
atom_id: AN-S-2586
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

Declare Projection.Updated At

## Claim

### Formal Claim

```CFEL
# model
Projection.Updated At{::1}:: [datetime]{::1};

Projection.Updated At.*[]{::0};

# instances
Projection//$projection.Updated At == MAX(Event Record//$event_record(.object_output{=1}, .object_output.version{=0}, .object_output.id = $projection.ID, (.action = create OR .action = update)).happened_at)
```

