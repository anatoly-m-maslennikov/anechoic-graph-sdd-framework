---
atom_family: SPEC
atom_id: AN-S-167
concern:
  subject: "Projection"
  path: "Model/Graph/Node//Artifact//Derived"
  relation: "is_narrower_than"
container:
  component: C16
tier: 1
context:
  lens: DES
state:
  status: active
  version: 21
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---
## Summary

Rebuild one programmatic Projection

# Rebuild one programmatic Projection

the framework **must** provide one deterministic Tool that rebuilds one registered programmatic Projection from its declared sources, writes `updated_at` **and** `source_frontier`, replaces the output atomically, **and** records the rebuild through the Work Journal Tool.
