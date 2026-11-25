---
atom_family: SPEC
atom_id: AN-S-1827
container:
  component: C58
tier: 3
context:
  template: action
  lens: DOM/MTD
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-25T19:30:51.191228+00:00"
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
