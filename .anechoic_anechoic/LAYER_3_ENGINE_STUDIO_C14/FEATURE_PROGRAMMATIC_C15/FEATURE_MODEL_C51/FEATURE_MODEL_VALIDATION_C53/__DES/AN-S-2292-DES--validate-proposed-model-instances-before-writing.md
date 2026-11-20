---
atom_family: SPEC
atom_id: AN-S-2292
structure:
  container:
    component: C53
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-13T15:38:33.283869+00:00'
---
## Summary

Validate proposed Model instances before writing

## Claim

### Prose Claim

Before writing a new or updated instance, validate the complete proposed instance against all applicable Model rules, including inherited rules. Reject undeclared Properties, incorrect value types, values outside the allowed set, and violations of cardinality or Relation constraints.

In a batch, validate each target before its write in the existing execution order. Write the first validation error to stderr and stop the operation. Earlier successful writes remain applied.
