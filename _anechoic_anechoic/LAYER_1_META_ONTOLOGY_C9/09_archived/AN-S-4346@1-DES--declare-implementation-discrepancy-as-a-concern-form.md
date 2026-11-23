---
atom_family: SPEC
atom_id: AN-S-4346
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: '2026-11-12T20:27:11.834911+00:00'
---
## Summary

Declare Implementation Discrepancy as a Concern Form

## Claim

### Prose Claim

Identify the applicable RMEDO Atom and the code location. State what the Atom specifies and what the code does.

Resolved means the code and applicable specification agree. Canceled means the recorded comparison is obsolete because the code or specification changed scope or was retired.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Concern

class ImplementationDiscrepancy(Concern):
    pass

declare_entity(entity_class=ImplementationDiscrepancy, entity_name='Implementation Discrepancy', qualification_property_path="Atom.Header.Context.Form")
```

## Semantics

An Implementation Discrepancy records a mismatch between the code and an applicable RMEDO Atom.
