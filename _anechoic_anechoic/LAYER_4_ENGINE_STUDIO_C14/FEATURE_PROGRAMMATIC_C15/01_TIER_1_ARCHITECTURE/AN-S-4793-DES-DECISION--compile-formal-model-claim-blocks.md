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
  - AN-S-4792@1
state:
  status: active
  version: 1
  updated_at: '2026-11-24T00:00:00+00:00'
---

## Summary

Compile formal Model Claim blocks

## Claim

### Prose Claim

The Formal Model Engine reads Claim fences, retains CFEL and compiles Python Model Claims. Its language selection is modeled below; the model does not establish implementation conformance.

### Formal Claim

```lean
inductive ClaimLanguage where
  | cfel | python | other
  deriving DecidableEq

def selected : ClaimLanguage → Bool
  | .cfel | .python => true
  | .other => false

theorem other_is_not_selected : selected .other = false := by rfl
```
