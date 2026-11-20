---
atom_family: SPEC
atom_id: AN-S-1709
structure:
  container:
    component: C9
  tier: 3
context:
  lens: SWD
state:
  status: active
  version: 22
  updated_at: 2026-11-02 08:06:47 +0400
---
## Summary

Write Workflow schemes using Step references

## Claim

### Prose Claim


Workflow schemes using Step references.


**to** write a Workflow scheme, express the graph through references **to** its Step Atoms:

- use **`=1`** unambiguous reference for **every** graph node; readable node labels **may** accompany those references.
- state the entry, declared Step order and structural Relations, Conditional Step routing, **and** terminal outcomes against those nodes.
- place Action references **and** parameter/input bindings **in** leaf Step Atoms rather than reproducing them **in** the scheme; a containing Step carries its nested substeps and no own Action launch.
- reference reusable Action behavior from the Steps; do **not** paste it into either the Step **or** graph Claim.
