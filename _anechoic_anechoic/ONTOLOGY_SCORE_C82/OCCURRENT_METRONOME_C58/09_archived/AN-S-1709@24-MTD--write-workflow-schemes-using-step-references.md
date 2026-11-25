---
atom_family: SPEC
atom_id: AN-S-1709
container:
  component: C58
tier: 3
context:
  lens: DOM/MTD
state:
  status: "archived"
  version: 24
  updated_at: "2026-11-25T20:06:05.080695+00:00"
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

State each transition's type and its result condition. Give each Workflow, Step, and Action its own primary contribution. For an Action, specify applicable inputs, preconditions, results, effects, and failures. For a leaf Step, name the one Workflow or Action it invokes and its parameter bindings.
