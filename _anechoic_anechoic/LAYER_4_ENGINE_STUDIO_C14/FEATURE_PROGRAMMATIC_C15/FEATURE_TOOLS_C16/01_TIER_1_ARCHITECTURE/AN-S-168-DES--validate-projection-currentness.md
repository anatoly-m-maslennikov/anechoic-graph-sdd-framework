---
atom_family: SPEC
atom_id: AN-S-168
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
  version: 23
  updated_at: "2026-11-27T16:16:01.404965+00:00"
---
## Summary

Validate Projection currentness

# Validate Projection currentness

the framework **must** provide one deterministic read-only Tool that validates one programmatic-generated **or** LLM-generated Projection's declared Projection Type, `updated_at`, `source_frontier`, source availability, **and** currentness **without** treating the Projection as independent authority.
