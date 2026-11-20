---
atom_family: SPEC
atom_id: AN-S-2048
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 5
  updated_at: '2026-11-12T17:23:54+00:00'
---
## Summary

Declare Analysis & Advisory

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Atom

class AnalysisAndAdvisory(Atom):
    pass

declare_entity(entity_class=AnalysisAndAdvisory, entity_name='Analysis and Advisory', qualification_property_path="Atom.Header.Context.Role", classifications={"Role Order Number": 2})
```

## Semantics

Analysis and Advisory covers analysis reports, rationales and spec proposals. It establishes findings, explanations, comparisons, reasons or proposed changes.

For reading historical Atom carriers, `Analysis & Advisory` is an alias for this same Role. New and updated Atom carriers use the canonical Role value `Analysis and Advisory`.
