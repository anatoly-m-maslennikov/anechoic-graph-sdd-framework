---
atom_family: TKT
atom_id: AN-T-2744
container:
  atom: AN-T-2483
priority: 2
context:
  template: task
state:
  status: done
  version: 1
  updated_at: '2026-11-13T19:14:49.644551+00:00'
---
## Summary

Implement Relation applicability and Property ordering

## Work

Update the Engine and MODEL_VALIDATION to read the declared endpoint levels and enforce Relation applicability and sibling order. Derive the canonical sibling order from the declared predecessor pairs, skip absent Properties, and derive the adjacency links for each bearer instance. Check same-bearer adjacency, predecessor and successor bounds, cycles, and both directions of INSTANCE_OF applicability. Coordinate with CA-P-3055 and CA-P-3061.

## Specification

CA-R-2247, CA-R-2965, CA-R-2476, CA-R-2473, CA-R-2967, CA-R-3083.

## Progress

The native parser fills in a missing level for each declared endpoint. The sibling validator derives order from predecessor pairs and skips absent fields. The generator rejects an ordering that fails to define a single chain.

The validator matches both endpoints against the same declared pair and reverses that pair for an inverse alias. Ordering rules bind to the declared bearer and applicable Role. The Model compiler, graph extractor and Workbench registry retain the reverse ordering alias. A registry rebuild from live sources resolved both HAS_INSTANCE and IS_ORDERED_RIGHT_BEFORE without reviving archived CA-R-2619.
