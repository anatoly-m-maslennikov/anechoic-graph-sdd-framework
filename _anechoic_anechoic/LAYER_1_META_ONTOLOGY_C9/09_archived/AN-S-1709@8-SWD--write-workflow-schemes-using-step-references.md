---
atom_family: SPEC
atom_id: AN-S-1709
container:
  component: C9
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 8
  updated_at: 2026-10-19 15:54:50 +0400
---
## Summary

Write Workflow schemes using Step references

# Summary

Write Workflow schemes using Step references

## Scope

Workflow schemes using Step references.

## Claim

**to** write a Workflow scheme, express the graph through references **to** its Step Atoms:

- use **`=1`** unambiguous reference for **every** graph node; readable node labels **may** accompany those references.
- state the entry, typed directed transitions, result conditions, **and** terminal outcomes against those nodes.
- place Action references **and** parameter/input bindings **in** the referenced Step Atoms rather than reproducing them **in** the scheme.
- reference reusable Action behavior from the Steps; do **not** paste it into either the Step **or** graph Claim.

## Details
