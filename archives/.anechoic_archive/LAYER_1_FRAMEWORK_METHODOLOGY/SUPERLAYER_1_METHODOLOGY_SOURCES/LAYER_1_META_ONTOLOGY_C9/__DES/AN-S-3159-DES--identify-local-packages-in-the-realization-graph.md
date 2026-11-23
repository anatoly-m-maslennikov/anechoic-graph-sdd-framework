---
atom_family: SPEC
atom_id: AN-S-3159
container:
  component: C9
tier: 3
context:
  lens: DES
relations:
  IS_REFERENCE:
  - AN-S-2596
  - AN-S-3014@2
state:
  status: active
  version: 2
  updated_at: '2026-11-20T23:12:09.705525+00:00'
---

## Summary

Identify local Packages in the Realization Graph

## Claim

### Prose Claim

- A local folder with a direct executable has one Package node across all languages.
- A Test Package has direct executable tests. Its target can be a Package or a Component.
- Use the common Package structure and the Package node kind.
