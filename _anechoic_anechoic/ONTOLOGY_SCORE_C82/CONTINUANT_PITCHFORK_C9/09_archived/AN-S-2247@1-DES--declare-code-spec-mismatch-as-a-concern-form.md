---
atom_family: SPEC
atom_id: AN-S-2247
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: '2026-11-13T15:51:57.445442+00:00'
---
## Summary

Declare Code-Spec Mismatch as a Concern Form

## Claim

### Prose Claim

Identify the applicable RMEDO Atom and the code location. State what the Atom specifies and what the code does.

Resolved means the code and applicable specification agree. Canceled means the recorded comparison is obsolete because the code or specification changed scope or was retired.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Concern

class CodeSpecMismatch(Concern):
    pass

declare_entity(entity_class=CodeSpecMismatch, entity_name='Code-Spec Mismatch', qualification_property_path="Atom.Header.Context.Form")
```

## Semantics

An Code-Spec Mismatch records a mismatch between the code and an applicable RMEDO Atom.
