---
atom_family: SPEC
atom_id: AN-S-3661
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 20
  updated_at: 2026-10-29 07:17:17 +0400
---
## Summary

Define the Step Operations Atom Type

# Summary

Define the Step Operations Atom Type

## Scope

the Step Type of Operations Atoms.

## Claim

the Operations Atom Type Step **means** the Type of an Operations Atom whose Claim defines **`=1`** Workflow node. a leaf Step, including a leaf substep, defines invocation of **`=1`** referenced reusable Action with its parameters **and** input bindings; a containing Step with nested substeps defines no own Action launch.

## Details

- a substep is a nested Step, not a separate Type.
- a Linear Step has ordered nonconditional substeps and no conditional substeps.
- a Conditional Step chooses **exactly one** branch in its own definition from its declared result condition and **may** use Actor input; result-based routing belongs to that definition.
- different Steps **may** reference the same Action with different bindings **without** copying or redefining that Action.
