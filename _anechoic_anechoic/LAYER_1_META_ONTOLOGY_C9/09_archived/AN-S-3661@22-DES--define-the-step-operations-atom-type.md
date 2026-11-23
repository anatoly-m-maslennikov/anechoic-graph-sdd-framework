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
  version: 22
  updated_at: 2026-10-29 17:09:47 +0400
---
## Summary

Define the Step Operations Atom Type

## Claim scope

the Step Type of Operations Atoms.

## Claim


A leaf Step launches exactly one referenced Action or Workflow with its parameters and input bindings. A Sub-step launches an Action only. A Step containing ordered Sub-steps has no Action or Workflow call of its own; a Sub-step cannot contain further Sub-steps.

## Details

- a substep is a nested Step, not a separate Type.
- a Linear Step has ordered nonconditional substeps and no conditional substeps.
- a Conditional Step chooses **exactly one** branch in its own definition from its declared result condition and **may** use Actor input; result-based routing belongs to that definition.
- different Steps **may** reference the same Action with different bindings **without** copying or redefining that Action.
