---
identity:
  atom_id: AN-T-44
context:
  container:
    component: C00
  tier: 3
  template: question
state:
  status: active
  version: 1
  updated_at: 2026-10-29 11:08:59 +0400
---
## Summary

Where should stable Scope Unit IDs be carried?

## Question

Which existing or new Project Structure encoding should persist Scope Unit identity separately from mutable Name, Label and Path?

## Details

Keep the adopted logical Scope Unit.ID definition and its string cardinality, but preserve the existing governing-configuration bytes and registered Scope Unit Name references. R1988 expressly adds no storage field or rename procedure; the latest 48-hour decisions do not specify a concrete migration protocol. Do not invent a new TOML key, allocate IDs to excluded Engine Scope Units, or revise the Scope Unit structure in this methodology-only Epic. Define the concrete ID encoding/data migration in the already separate Engine/Scope Unit work before requiring it from those readers.
