---
atom_family: SPEC
atom_id: AN-S-1176
container:
  component: C16
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 20
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---
## Summary

Patch project settings

# Patch project settings

the framework **must** provide one deterministic Tool that applies a schema-validated key-level patch **to** project settings, preserves unrelated values, emits the exact effective diff, **and** rejects direct edits **to** values declared as generated.
