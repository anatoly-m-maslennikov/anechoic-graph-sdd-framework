---
atom_family: SPEC
atom_id: AN-S-1167
container:
  component: C16
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 8
  updated_at: 2026-08-30 16:44:07 +0400
---
## Summary

Validate generated-data stage pipelines

# Validate generated-data stage pipelines

the framework **must** provide a deterministic Tool that validates the registered `src → stg → mrt → biz` prefixes, forward-only dependencies, declared source frontiers, **and** the separation of generated outputs from semantic authority.
