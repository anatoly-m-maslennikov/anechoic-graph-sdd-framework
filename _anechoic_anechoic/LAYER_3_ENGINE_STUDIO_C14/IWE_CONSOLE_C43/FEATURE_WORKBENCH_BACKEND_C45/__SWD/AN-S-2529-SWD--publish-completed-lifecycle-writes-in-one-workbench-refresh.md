---
atom_family: SPEC
atom_id: AN-S-2529
container:
  component: C45
tier: 5
context:
  lens: SWD
state:
  status: active
  version: 1
  updated_at: '2026-11-13T19:27:59.851737+00:00'
---
## Summary

Publish completed lifecycle writes in one Workbench refresh

## Claim scope

Independent lifecycle batch targets.

## Claim

### Prose Claim

Collect the paths changed by independent Archive or Promote Draft targets and refresh them together. Include completed file effects when a later target fails. Report a publication error separately when the files were written but Workbench could not refresh them.
