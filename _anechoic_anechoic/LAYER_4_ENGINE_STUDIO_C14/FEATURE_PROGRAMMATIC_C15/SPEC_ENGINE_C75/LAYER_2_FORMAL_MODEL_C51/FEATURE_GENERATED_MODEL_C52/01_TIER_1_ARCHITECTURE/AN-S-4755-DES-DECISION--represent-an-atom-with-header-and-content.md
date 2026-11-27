---
atom_family: SPEC
atom_id: AN-S-4755
container:
  component: C52
tier: 1
context:
  template: DECISION
  lens: DES
relations:
  IS_SOLUTION_FOR:
  - AN-S-3311@2
state:
  status: active
  version: 1
  updated_at: '2026-11-24T00:00:00+00:00'
---

## Summary

Represent an Atom with Header and Content.

## Claim

### Prose Claim

The bundled Atom class contains distinct Header and Content fields. Plan
inherits these fields from Atom. The formal claim models this shared shape;
it does not prove that the Python implementation conforms to the model.

### Formal Claim

```lean
structure AtomShape (Header Content : Type) where
  header : Header
  content : Content

def PlanShape (Header Content : Type) := AtomShape Header Content

theorem plan_has_atom_fields {Header Content : Type} (plan : PlanShape Header Content) :
    ∃ (header : Header) (content : Content), plan.header = header ∧ plan.content = content := by
  exact ⟨plan.header, plan.content, rfl, rfl⟩
```

## Details

The implementation defines Atom and Plan in
`FEATURE_GENERATED_MODEL_C52__shared.py` and the field classes in
`atom_fields.py`.
