---
atom_family: SPEC
atom_id: AN-S-2264
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Declare CORE_META_MODEL

## Claim


### Prose Claim

Additional HAS_ACTIVE_SUBJECT permissions for local Atoms in CORE_META_MODEL are exactly these finite typed selections:

- `MODEL//ANECHOIC <+ (Workspace, Workspace.native_thread_id, Workspace.project_root)`;
- `MODEL//ANECHOIC <+ (View, View.id, View.sql, View.name)`;



No unlisted descendants or other type members are admitted. An unresolved address grants no admission.


The Workspace and View grouped selections enumerate only the endpoint and Property objects declared by R2792 and R2793. These finite selections admit no other descendants or type members. Their Declaration ownership includes exactly those listed objects.

### Formal Claim

```CFEL
# instances
Scope Unit//CORE_META_MODEL.ID == "CA-SU-11";

Scope Unit//CORE_META_MODEL.Name == "CORE_META_MODEL";

Scope Unit//CORE_META_MODEL.Label == "LAYER";

Scope Unit//CORE_META_MODEL.order.ordered == true;

Scope Unit//CORE_META_MODEL.order.number == 1;

Scope Unit//CORE_META_MODEL ((IS_CONTAINED_BY)) Scope Unit//METHODOLOGY_SOURCES
```
