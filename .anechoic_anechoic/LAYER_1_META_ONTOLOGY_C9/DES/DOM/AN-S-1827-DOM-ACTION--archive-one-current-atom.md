---
identity:
  atom_id: AN-S-1827
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

Archive one Current Atom

## Claim scope

One exact selected Current Atom. The caller handles any contained Atoms through separate invocations under CA-R-1521. Archived inputs, inferred replacements, and overwrites are invalid.

## Claim

Archive the selected Current Atom using its applicable status model and derived carrier location. Preserve Version and Updated At. Report an explicit error on failure. An actual business observation may be recorded in the Journal independently; a recording failure does not block archival.

For missing or invalid input format or allowed value, give a short explanation and request an additional input dictionary. Wait for it; the caller may cancel while waiting, without interrupting an Action.

### Outputs

`savedArchivedAtom` a request for additional input, or an explicit failure; any Journal warning is separate.
