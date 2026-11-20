---
atom_family: SPEC
atom_id: AN-S-2069
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 7
  updated_at: '2026-11-12T12:33:04.158402+00:00'
---
## Summary

Declare Atom/(.Role := Requirement)/(.Form := Declaration)

## Claim

### Prose Claim


A Declaration states the applicable contract for its active Subject. Its Claim may contain several prose statements, Python formal expressions, or both when they form one coherent declaration about one topic.

Scope Unit Declaration is a Requirement Form using this template. It is not another Atom Role.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Requirement

class Declaration(Requirement):
    pass

declare_entity(
    entity_class=Declaration,
    entity_name='Declaration',
    qualification_property_path='Atom.Header.Context.Form',
)
```
