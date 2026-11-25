---
atom_family: SPEC
atom_id: AN-S-2706
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 8
  updated_at: "2026-11-25T22:46:55.601957+00:00"
---
## Summary

Define scalar Value Format

## Claim

### Prose Claim


The scalar Value Format admits a direct primitive value, including string,
numeric, Boolean, date/time and null values supported by the declared Carrier.
Sequences and mappings remain Carrier structures: sequence members are counted
individually, while child mapping keys are not direct values of their parent.
Specific Formats can restrict this broad domain.



### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import ValueFormat

class ScalarValueFormat(ValueFormat):
    pass

declare_entity(entity_name='scalar', entity_class=ScalarValueFormat)
```
