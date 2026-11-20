---
atom_family: SPEC
atom_id: AN-S-1375
structure:
  container:
    component: C46
  tier: 5
context:
  lens: QA
state:
  status: draft
  version: 5
  updated_at: '2026-11-14T07:53:31.737631+00:00'
---
## Summary

Verify the shared View rename modal

## Claim

### Prose Claim

Verify that double-clicking a View name or choosing Rename View in the palette
opens the same modal with the displayed name prefilled.

## Details

- Confirm renames the View and survives refresh or reload.
- Cancel, Escape, single clicks, and unrelated query or autosave leave
  the name unchanged.
