---
atom_family: SPEC
atom_id: AN-S-1167
container:
  component: C16
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 19
  updated_at: 2026-10-27 19:59:50 +0400
---
## Summary

Validate generated-data stage pipelines

# Validate generated-data stage pipelines

the framework **must** provide a deterministic Tool that validates the registered `src → stg → mrt → biz` prefixes, forward-only dependencies, declared source frontiers, **and** the separation of generated outputs from semantic authority.
