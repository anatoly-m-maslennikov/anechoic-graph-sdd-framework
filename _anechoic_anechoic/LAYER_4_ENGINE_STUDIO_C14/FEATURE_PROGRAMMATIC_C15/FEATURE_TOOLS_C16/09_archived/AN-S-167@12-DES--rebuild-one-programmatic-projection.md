---
atom_family: SPEC
atom_id: AN-S-167
container:
  component: C16
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 12
  updated_at: 2026-10-24 00:06:46 +0400
---
## Summary

Rebuild one programmatic Projection

# Rebuild one programmatic Projection

the framework **must** provide one deterministic Tool that rebuilds one registered programmatic Projection from its declared sources, writes `updated_at` **and** `source_frontier`, replaces the output atomically, **and** records the rebuild through the Work Journal Tool.
