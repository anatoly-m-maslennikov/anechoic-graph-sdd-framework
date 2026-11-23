---
atom_family: SPEC
atom_id: AN-S-2589
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-11-03 20:00:05 +0400
---
## Summary

Declare Atom.Header.Updated At

## Claim

### Formal Claim

```CFEL
# model
Atom.Header.State.Updated At{::1}:: [datetime]{::1};

Atom.Header.State.Updated At.*[]{::0};

# instances
Atom//$atom.Header.State.Updated At == MAX(Event Record//$event_record(.object_output{=1}, .object_output.version{=1}, .object_output.id = $atom.Header.Identity.ID, .object_output.version = $atom.Header.State.Version, (.action = create OR .action = update)).happened_at)
```
