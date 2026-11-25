---
atom_family: SPEC
atom_id: AN-S-1826
container:
  component: C58
tier: 3
context:
  template: action
  lens: DOM/MTD
state:
  status: "active"
  version: 2
  updated_at: "2026-11-25T19:30:51.024807+00:00"
---
## Summary

Apply one Direct Atom Update

## Claim scope

One exactly selected non-container Atom and its requested changes.

## Claim

Resolve the selected Draft, Current or Archived Atom and apply supplied property changes in place, carrying omitted properties forward. Derive the carrier filename and location from the resulting properties and model. Preserve Version. Set Updated At to the edit time when a supplied property changes. Apply the edit without semantic change classification. Report an explicit error on failure. An actual business observation may be recorded in the Journal independently; a recording failure does not block the edit.

For missing or invalid input format or allowed value, give a short explanation and request an additional input dictionary. Wait for it; the caller may cancel while waiting, without interrupting an Action.

### Outputs

`savedAtom` a request for additional input, or an explicit failure; any Journal warning is separate.
