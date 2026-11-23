---
atom_family: SPEC
atom_id: AN-S-175
container:
  component: C16
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 15
  updated_at: 2026-10-24 20:48:49 +0400
---
## Summary

Validate an artifact catalog

# Validate an artifact catalog

the framework **must** provide one deterministic read-only Tool that compares a registered artifact catalog with its declared authoritative source frontier **and** fails closed on missing, stale, duplicate, unknown, **or** inconsistent entries.
