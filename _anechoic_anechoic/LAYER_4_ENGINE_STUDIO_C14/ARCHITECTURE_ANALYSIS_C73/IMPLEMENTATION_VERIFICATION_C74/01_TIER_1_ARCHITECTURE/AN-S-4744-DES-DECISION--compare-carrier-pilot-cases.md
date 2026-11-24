---
atom_family: SPEC
atom_id: AN-S-4744
container:
  component: C74
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4743
state:
  status: active
  version: 1
  updated_at: '2026-11-24T00:00:00+00:00'
---
## Summary

Compare carrier pilot cases

## Claim

### Prose Claim

Generate the carrier model, collect source and effect evidence, run Lean against the supplied formal blocks, and compare the selected observations. An unavailable Lean executable or failed comparison is unresolved. Findings are limited to the selected cases.

### Formal Claim

The following claim models only the stated relation; it does not prove the implementation conforms.

```lean
theorem failed_comparison_unresolved (leanAvailable comparisonValid : Bool)
    (h : leanAvailable = false ∨ comparisonValid = false) :
    (leanAvailable && comparisonValid) = false := by
  cases leanAvailable <;> cases comparisonValid <;> simp_all
```
