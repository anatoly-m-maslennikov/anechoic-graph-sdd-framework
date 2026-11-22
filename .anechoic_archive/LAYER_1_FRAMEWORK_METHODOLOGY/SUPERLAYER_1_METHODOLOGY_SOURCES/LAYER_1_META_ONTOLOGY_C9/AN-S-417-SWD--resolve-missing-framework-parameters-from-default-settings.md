---
atom_family: SPEC
atom_id: AN-S-417
container:
  component: C9
tier: 2
context:
  lens: SWD
state:
  status: active
  version: 24
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary
Resolve missing framework parameters from Default Settings

## Claim

### Prose Claim

resolution of a Framework Instance Settings parameter.

**to** resolve a Framework Instance Settings parameter, use its explicit value **if** that parameter is present **in** the current Project's Framework Instance Settings; **otherwise**, use the corresponding value from Default Settings. determine presence for the individual parameter, **not** its containing section **or** the truthiness of its value, so valid `false`, `0`, **and** empty values remain explicit selections. validate the selected value against its governing parameter authority **and** reject an invalid explicit value **without** falling back. **if** neither source supplies a required parameter, report that parameter as unresolved **and** stop the operation that requires it; an optional parameter **may** remain absent. do **not** copy inherited values into Framework Instance Settings as explicit selections.
