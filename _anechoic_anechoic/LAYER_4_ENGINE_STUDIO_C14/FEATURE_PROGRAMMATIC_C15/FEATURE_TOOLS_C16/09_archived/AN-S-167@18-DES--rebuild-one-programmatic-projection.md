---
atom_family: SPEC
atom_id: AN-S-167
container:
  component: C16
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 18
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Rebuild one programmatic Projection

# Rebuild one programmatic Projection

the framework **must** provide one deterministic Tool that rebuilds one registered programmatic Projection from its declared sources, writes `updated_at` **and** `source_frontier`, replaces the output atomically, **and** records the rebuild through the Work Journal Tool.
