---
atom_family: SPEC
atom_id: AN-S-5033
container:
  component: C52
tier: 0
context:
  template: solution
  lens: DES
relations:
  ANSWERS:
  - AN-S-3066@9-draft
state:
  status: draft
  version: 1
  updated_at: '2026-11-27T00:00:00+00:00'
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

