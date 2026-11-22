---
atom_family: SPEC
atom_id: AN-S-175
container:
  component: C16
tier: 1
context:
  lens: DES
state:
  status: active
  version: 18
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Validate an artifact catalog

# Validate an artifact catalog

the framework **must** provide one deterministic read-only Tool that compares a registered artifact catalog with its declared authoritative source frontier **and** fails closed on missing, stale, duplicate, unknown, **or** inconsistent entries.
