---
atom_family: SPEC
atom_id: AN-S-2333
container:
  component: C58
tier: 5
context:
  lens: DOM/MTD
state:
  status: active
  version: 33
  updated_at: '2026-11-25T21:00:38.544763+00:00'
---
## Summary

Resolve implementation retry limits by source precedence

## Claim

### Prose Claim

These cases describe the legacy Plan and Hub retry configuration. A native Atom Header follows AN-S-3160.


an effective Implementation Retry Limit resolved from direct Operator input, a Plan, the nearest Hub, Framework Instance Settings, **or** Default Settings.


**to** resolve an effective Implementation Retry Limit, select the first applicable explicit source **in** this precedence:

1. direct Operator input for the current execution context.
2. the current Plan's explicit Implementation Retry Limit.
3. the nearest Hub with an explicit limit, walking `IS_CONTAINED_BY` from nearest **to** farthest **and** reading its own current Plan File Carrier under AN-S-1772@30.
4. Framework Instance Settings, resolving an omitted instance parameter through Default Settings under CA-M-279-CORE_META_MODEL-IMPLEMENTATION_METHOD--resolve-missing-framework-parameters-from-default-settings.

### resolution constraints

- an omitted optional retry override preserves inheritance; another explicit field does **not** stop this lookup. a missing mandatory Plan file is invalid, **not** an inherited-setting selection.
- determine presence, **not** truthiness: **`=0`** is an explicit limit.
- an invalid **or** ambiguous reached source requires Operator disposition **without** silent fallback; an absent effective value stops the affected retry decision.
- direct Operator input applies **only** within its stated context.
- do **not** copy inherited values **or** create separate Objective/settings files. retain explicit overrides even **when** equal **to** the inherited value.
- use the same Plan identity for a Hub's file **and** folder.
- resolution does **not** reset the consumed retry count governed by CA-O-024-CORE_META_MODEL-ACTION--control-implementation-retries.
