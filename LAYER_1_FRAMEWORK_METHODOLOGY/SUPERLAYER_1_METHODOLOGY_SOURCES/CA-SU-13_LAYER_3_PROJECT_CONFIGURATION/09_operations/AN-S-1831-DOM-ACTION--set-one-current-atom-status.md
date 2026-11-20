---
identity:
  atom_id: AN-S-1831
context:
  container:
    component: C9
  tier: 3
  lens: DES/DOM
  template: action
state:
  status: active
  version: 1
  updated_at: 2026-11-11 14:05:36 +0400
---
## Summary

Set one Current Atom Status

## Claim scope

One exact Current Atom and one requested Status in its qualified model's Current group.

## Claim

Set the selected Current Atom's Status to the supplied value allowed by its applicable Current status model. Derive carrier location; preserve Version and Updated At. Report an explicit error on failure. Journal business observations are independent and nonblocking.

For missing or invalid input format or allowed value, give a short explanation and request an additional input dictionary. Wait for it; the caller may cancel while waiting, without interrupting an Action.

### Outputs

`savedCurrentAtom` a request for additional input, or an explicit failure; any Journal warning is separate.
