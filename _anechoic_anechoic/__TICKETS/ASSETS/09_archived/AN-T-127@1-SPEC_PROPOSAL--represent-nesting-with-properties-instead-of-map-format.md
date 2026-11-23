---
atom_family: TKT
atom_id: AN-T-127
container:
  component: C00
priority: 2
context:
  template: spec_proposal
state:
  status: archived
  version: 1
  updated_at: 2026-10-29 02:57:48 +0400
---
## Summary

Represent nesting with properties instead of map Format

# Summary

Represent nesting with properties instead of map Format

## Decision

Remove map from the proposed value Formats. Declared child properties describe nested structure; a YAML mapping is its carrier representation, not a separate value Format. The earlier removal of list remains in effect.

```text
subjects{0}
subjects.governs[string]{1}
subjects.depend_on[string]{0+}
```

The grouping property has no direct values. Each child keeps its own value format and cardinality. This changes neither nesting nor the existing YAML subjects.depends_on spelling. Arbitrary-key dictionary semantics are not introduced by this decision.

## State

The main Model proposal and Value Format Definition Draft omit map. Current methodology, configuration, implementation and runtime are unchanged.
