---
atom_family: SPEC
atom_id: AN-S-1831
container:
  component: C58
tier: 3
context:
  template: action
  lens: DOM/MTD
state:
  status: "active"
  version: 2
  updated_at: "2026-11-25T19:30:52.023148+00:00"
---
## Summary

Set one Current Atom Status

## Claim scope

One exact Current Atom and one requested Status in its qualified model's Current group.

## Claim

Set the selected Current Atom's Status to the supplied value allowed by its applicable Current status model. Derive the carrier location. Preserve Version. Set Updated At to the edit time for a Status change. Report an explicit error on failure. Journal business observations are independent and nonblocking.

For missing or invalid input format or allowed value, give a short explanation and request an additional input dictionary. Wait for it; the caller may cancel while waiting, without interrupting an Action.

### Outputs

`savedCurrentAtom` a request for additional input, or an explicit failure; any Journal warning is separate.
