---
identity:
  atom_id: AN-S-1709
context:
  container:
    component: C9
  tier: 3
  lens: SWD
state:
  status: draft
  version: 23
  updated_at: 2026-11-05 02:57:58 +0400
---
## Summary

Write Workflow schemes using Step references

## Claim

### Prose Claim


Workflow schemes using Step references.


**to** write a Workflow scheme, express the graph through references **to** its Step Atoms:

- use **`=1`** unambiguous reference for **every** graph node; readable node labels **may** accompany those references.
- state the entry, declared Step order and structural Relations, Conditional Step routing, **and** terminal outcomes against those nodes.
- place each leaf Step’s single Action reference **or** Workflow call **and** its parameter/input bindings **in** that Step Atom rather than reproducing them **in** the scheme. A leaf Step RUNS exactly one Action **or** exactly one Workflow; its bindings use only previous Step outputs, the enclosing Workflow Run input, **or** values fixed by that Step. A containing Step carries its nested Steps and launches neither an Action nor a Workflow. Each binding references the selected Action or Workflow contract; it does not copy or redefine that contract.
- reference reusable Action behavior from the Steps; do **not** paste it into either the Step **or** graph Claim.
