---
atom_family: SPEC
atom_id: AN-S-2583
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 8
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Use full Scope Unit names in filenames

# Summary

Use full Scope Unit names in filenames

## Scope

Scope Unit references serialized **in** Atom filenames **in** the ANECHOIC Project.

## Claim

**every** filename token representing a Scope Unit **must** use its complete Scope Unit Name, rendered **in** uppercase with underscores under `CA-D-284-CORE_META_MODEL-DELIVERY--serialize-filename-token-case`, **without** abbreviation **or** a separately maintained alias.

## Details

this selects the representation required by `CA-D-302-CORE_META_MODEL-DELIVERY--serialize-scope-unit-references-as-filename-tokens`. `CORE_META_MODEL` remains `CORE_META_MODEL`; `PROJECT_CONFIGURATION` remains `PROJECT_CONFIGURATION`. the Scope Unit Name is the source; the filename token is its representation.
