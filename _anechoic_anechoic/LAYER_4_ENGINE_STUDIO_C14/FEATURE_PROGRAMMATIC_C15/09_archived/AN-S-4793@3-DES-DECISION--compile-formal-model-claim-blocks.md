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
  status: "archived"
  version: 3
  updated_at: "2026-11-27T20:43:50.902996+00:00"
---

## Summary

Compile formal Model Claim blocks

## Claim

### Prose Claim

The Formal Model Engine reads Claim fences and compiles Python Model Claims. Its language selection is modeled below; the model does not establish implementation conformance.

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
