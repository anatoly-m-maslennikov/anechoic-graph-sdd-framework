---
atom_family: SPEC
atom_id: AN-S-4793
container:
  component: C15
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-4792@3
state:
  status: "active"
  version: 5
  updated_at: "2026-11-27T20:43:50.902996+00:00"
---

## Summary

Compile formal Model Claim blocks

## Claim

### Prose Claim

The Formal Model Engine reads Claim fences and compiles the selected
Model Claims.

### Formal Claim

```lean
inductive ClaimLanguage where
  | python | other
  deriving DecidableEq

def selected : ClaimLanguage → Bool
  | .python => true
  | .other => false

theorem other_is_not_selected : selected .other = false := by rfl
```

## Semantics

The predicate models language selection. Implementation conformance
requires separate evidence.
