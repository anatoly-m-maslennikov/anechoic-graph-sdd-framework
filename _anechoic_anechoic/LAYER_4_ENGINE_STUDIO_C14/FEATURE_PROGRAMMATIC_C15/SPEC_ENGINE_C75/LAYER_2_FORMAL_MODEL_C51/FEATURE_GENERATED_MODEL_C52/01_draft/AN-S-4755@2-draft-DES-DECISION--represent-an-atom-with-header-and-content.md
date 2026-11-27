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
  - AN-S-3311@3-draft
state:
  status: draft
  version: 2
  updated_at: '2026-11-25T10:53:53.766836+00:00'
---

## Summary

Represent an Atom with Header and Content.

## Claim

### Prose Claim

Header and Content stand for the bundled field types. Plan uses Atom's field
definitions unchanged.

### Formal Claim

```python shape
class Atom:
    header: Header
    content: Content


class Plan(Atom):
    pass
```

## Details

The implementation defines Atom and Plan in
`FEATURE_GENERATED_MODEL_C52__shared.py` and the field classes in
`atom_fields.py`.
