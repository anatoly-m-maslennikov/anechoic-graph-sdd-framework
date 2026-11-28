---
atom_family: SPEC
atom_id: AN-S-5047
concern:
  subject: Module
  path: Model/Graph/Node//Artifact//SSOT//Realization/Content
  relation: is_contained_by
container:
  component: C15
tier: 0
context:
  template: STANDARD
  lens: SWD/SWCS
state:
  status: "active"
  version: 3
  updated_at: "2026-11-27T20:35:14.221449+00:00"
---

## Summary

Author web source in TypeScript

## Semantics

This selection applies to authored PROGRAMMATIC web source, including script
blocks in Svelte components. It does not make generated outputs authored
source. Existing typed lint coverage remains governed by AN-S-3359@2.

## Claim

### Formal Claim

```lean
namespace ProgrammaticWebLanguage

def conforms (authoredWeb : Bool) (language : String) : Bool :=
  !authoredWeb || language == "typescript"

end ProgrammaticWebLanguage
```
