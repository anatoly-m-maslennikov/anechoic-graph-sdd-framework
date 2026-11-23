---
atom_family: SPEC
atom_id: AN-S-2625
container:
  component: C43
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 5
  updated_at: 2026-11-09 17:00:18 +0400
---

## Summary

Declare CODEX_EXTENSION

## Claim

### Prose Claim

The receiving Scope Unit is CODEX_EXTENSION. Existing default Role and Form admissions remain applicable. The additional local Role/Form pairs are exactly:

- Delivery / Solution;
- Method / Solution;
- Requirement / Rule;

The admitted HAS_ACTIVE_SUBJECT targets are exactly the declared entities or instances at these addresses:

- `ANECHOIC_MODEL <+ View`;
- `ANECHOIC_MODEL <+ Workspace`;
- `ANECHOIC_STRUCTURE <+ Aspects <+ Engineering <+ Development <+ Architecture <+ Communication <+ Interface Contracts`;

Each address selects one endpoint object, not the address string, other members of its type or descendants. An unresolved address is diagnostic and grants no admission. These permissions apply only to local Atoms whose Header.Container resolves to CODEX_EXTENSION. The Scope Unit identity, Parent, responsibility and structural tree are unchanged.

### Formal Claim

```CFEL
# instances
Scope Unit//CODEX_EXTENSION.ID == "CA-SU-48";
Scope Unit//CODEX_EXTENSION.Name == "CODEX_EXTENSION";
Scope Unit//CODEX_EXTENSION.Label == "FEATURE";
Scope Unit//CODEX_EXTENSION.order.ordered == false;
Scope Unit//CODEX_EXTENSION ((IS_CONTAINED_BY)) Scope Unit//WORKBENCH
```
