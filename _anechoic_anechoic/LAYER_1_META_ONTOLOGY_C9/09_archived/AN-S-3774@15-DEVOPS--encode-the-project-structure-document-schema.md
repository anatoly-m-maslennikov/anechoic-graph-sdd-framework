---
atom_family: SPEC
atom_id: AN-S-3774
container:
  component: C9
tier: 2
context:
  lens: DevOps
state:
  status: archived
  version: 15
  updated_at: 2026-10-24 10:48:25 +0400
---
## Summary

Encode the Project Structure document schema

# Summary
Encode the Project Structure document schema

## Scope
Project Structure TOML documents, including declared non-Project Scope Units **and** the implicit root Project.

## Claim

the Project Structure TOML document **must** contain the integer `schema_version = 1` **and** **`=1`** `scope_units` array of tables, with **`>=0`** rows for declared non-Project Scope Units. an empty array **must** use `scope_units = []`; nonempty arrays use `[[scope_units]]`. the root Project is implicit from Project Settings **and** **must not** have a duplicate row. unknown top-level keys, unknown row keys, duplicate TOML keys, **and** unsupported schema versions **must** be rejected rather than ignored. document comments **may** explain authority **and** retained readability fields, **without** introducing additional authoritative fields.

## Details
