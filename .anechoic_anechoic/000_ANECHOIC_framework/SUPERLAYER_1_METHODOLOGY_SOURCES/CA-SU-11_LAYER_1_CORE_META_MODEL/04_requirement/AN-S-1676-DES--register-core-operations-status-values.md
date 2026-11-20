---
identity:
  atom_id: AN-S-1676
context:
  container:
    component: C9
  tier: 2
  lens: DES
state:
  status: active
  version: 19
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Register Core Operations Status Values

## Claim

### Prose Claim


the default Status value domain of Operations Atoms with Type Workflow, Step, or Action.


the Core allowed values of Operations Status **must** be exactly (Draft, Active, Archived); that one Content Role Status model applies to Operations Atoms with Type Workflow, Step, or Action unless an admitted Extension or Project Configuration establishes a more-specific Status domain under that exact Content Role and Type path.

## Details

this Status is the Artifact Revision Property of the Operations Atom itself. it does **not** define a Status transition, carrier placement, setting, or a Workflow, Step, or Action Run outcome, receipt, retry state, result, or completion state.
