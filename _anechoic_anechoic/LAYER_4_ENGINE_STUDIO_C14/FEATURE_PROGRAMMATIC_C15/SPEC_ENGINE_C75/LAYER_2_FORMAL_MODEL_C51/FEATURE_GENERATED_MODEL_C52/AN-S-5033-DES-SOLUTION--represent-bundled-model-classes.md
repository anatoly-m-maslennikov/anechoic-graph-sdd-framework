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
  - AN-S-3066@10
state:
  status: active
  version: 2
  updated_at: '2026-11-27T01:04:20.461163+00:00'
---

## Summary

Represent an Atom with AtomHeader and AtomContent.

## Claim

### Prose Claim

AtomHeader and AtomContent are the bundled field types. Plan uses Atom's
field definitions unchanged. The shape profile omits Atom's own base and
dataclass field metadata.

### Formal Claim

```python shape
class Atom:
    header: AtomHeader
    content: AtomContent


class Plan(Atom):
    pass
```

