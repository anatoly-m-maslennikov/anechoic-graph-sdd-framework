---
identity:
  atom_id: AN-S-1678
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: active
  version: 12
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Enable containment for Plan Atoms

## Claim

### Prose Claim


Containment capability of Plan Atoms.


`Atom/(.Header.Role := Plan).Enabled Relations.Contains` **must** be True. a Plan Atom **may** contain other Plan Atoms.

## Details

Plan labels such as Epic, Task and Version do not create different containment Types. Containment is optional and can nest. This permission does not implement a Plan projection or replace other typed relations between Plans.
