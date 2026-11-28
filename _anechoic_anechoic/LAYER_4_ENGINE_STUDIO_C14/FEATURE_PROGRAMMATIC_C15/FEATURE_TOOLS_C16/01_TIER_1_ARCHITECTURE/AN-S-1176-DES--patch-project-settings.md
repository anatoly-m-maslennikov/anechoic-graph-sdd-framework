---
atom_family: SPEC
atom_id: AN-S-1176
concern:
  subject: "TOML"
  path: Model/Carrier/Filesystem/File//Non-executable File
  relation: "is_narrower_than"
container:
  component: C16
tier: 1
context:
  lens: DES
state:
  status: active
  version: 22
  updated_at: "2026-11-28T11:52:02.110048+00:00"
---
## Summary

Patch project settings

# Patch project settings

the framework **must** provide one deterministic Tool that applies a schema-validated key-level patch **to** project settings, preserves unrelated values, emits the exact effective diff, **and** rejects direct edits **to** values declared as generated.
