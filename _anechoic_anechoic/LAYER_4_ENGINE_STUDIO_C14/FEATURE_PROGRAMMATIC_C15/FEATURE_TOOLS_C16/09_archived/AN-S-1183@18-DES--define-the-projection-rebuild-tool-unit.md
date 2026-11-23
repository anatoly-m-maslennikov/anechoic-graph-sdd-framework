---
atom_family: SPEC
atom_id: AN-S-1183
container:
  component: C16
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 18
  updated_at: 2026-10-23 03:17:34 +0400
---
## Summary

Define the PROJECTION_REBUILD Tool unit

# Define the PROJECTION_REBUILD Tool unit

`PROJECTION_REBUILD` **must** be one Doer Tool owned immediately by `TOOLS` as an `unordered_unit` at Structural level `4`, addressed by `102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/201_TOOLS/PROJECTION_REBUILD`, **and** realized under `102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/201_TOOLS/PROJECTION_REBUILD/`; it derives the complete affected Projection set from changed source frontiers, orders rebuilds by declared dependencies, previews **every** output effect, materializes **only** explicitly approved outputs, **and** verifies currentness **and** idempotence **after** publication.
