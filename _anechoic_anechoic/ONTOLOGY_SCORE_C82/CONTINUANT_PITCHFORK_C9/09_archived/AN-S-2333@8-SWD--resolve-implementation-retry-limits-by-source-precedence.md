---
atom_family: SPEC
atom_id: AN-S-2333
container:
  component: C9
tier: 3
context:
  lens: SWD
state:
  status: archived
  version: 8
  updated_at: 2026-09-22 23:02:20 +0000
---
## Summary

Resolve implementation retry limits by source precedence

# Summary

Resolve implementation retry limits by source precedence

## Claim

**to** resolve an effective Implementation Retry Limit, select the first applicable explicit source **in** this precedence:

1. direct Operator input for the current execution context.
2. the current Plan's explicit Implementation Retry Limit.
3. the nearest Hub with an explicit limit, walking `IS_DECOMPOSITION_OF` from nearest **to** farthest **and** reading its own current Plan File Carrier under CA-D-447.
4. Framework Instance Settings, resolving an omitted instance parameter through Default Settings under CA-M-279.

### resolution constraints

- an omitted optional retry override preserves inheritance; another explicit field does **not** stop this lookup. a missing mandatory Plan file is invalid, **not** an inherited-setting selection.
- determine presence, **not** truthiness: **=0** is an explicit limit.
- an invalid **or** ambiguous reached source requires Operator disposition **without** silent fallback; an absent effective value stops the affected retry decision.
- direct Operator input applies **only** within its stated context.
- do **not** copy inherited values **or** create separate Objective/settings files. retain explicit overrides even **when** equal **to** the inherited value.
- use the same Plan identity for a Hub's file **and** folder; ignore unrelated files **and** historical Revisions.
- resolution does **not** reset the consumed retry count governed by CA-O-024.
