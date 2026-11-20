---
identity:
  atom_id: AN-S-1826
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

Apply one Direct Atom Update

## Claim scope

One exactly selected non-container Atom and its requested changes.

## Claim

Resolve the selected Draft, Current or Archived Atom and apply supplied property changes in place, carrying omitted properties forward. Derive the carrier filename and location from the resulting properties and model. Preserve Version and Updated At; do not gate the edit on a semantic change classification. Report an explicit error on failure. An actual business observation may be recorded in the Journal independently; a recording failure does not block the edit.

For missing or invalid input format or allowed value, give a short explanation and request an additional input dictionary. Wait for it; the caller may cancel while waiting, without interrupting an Action.

### Outputs

`savedAtom` a request for additional input, or an explicit failure; any Journal warning is separate.
