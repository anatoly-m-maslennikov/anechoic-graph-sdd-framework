---
identity:
  atom_id: AN-S-2583
context:
  container:
    component: C9
  tier: 3
  lens: DevOps
state:
  status: active
  version: 14
  updated_at: 2026-11-03 23:25:51 +0400
---
## Summary

Use full Scope Unit names in filenames

## Claim

### Prose Claim


Scope Unit references serialized **in** Atom filenames **in** the ANECHOIC Project.


**every** filename token representing a Scope Unit **must** use its complete Scope Unit Name, rendered **in** uppercase with underscores under `CA-D-284-CORE_META_MODEL-DELIVERY--serialize-filename-token-case`, **without** abbreviation **or** a separately maintained alias.

## Details

this selects the representation required by `CA-D-302-CORE_META_MODEL-DELIVERY--serialize-scope-unit-references-as-filename-tokens`. `CORE_META_MODEL` remains `CORE_META_MODEL`; `PROJECT_CONFIGURATION` remains `PROJECT_CONFIGURATION`. the Scope Unit Name is the source; the filename token is its representation.
