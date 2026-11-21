---
atom_family: SPEC
atom_id: AN-S-2124
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 3
  updated_at: 2026-11-11 14:06:22 +0400
---
## Summary

Declare Projection/(.Form := Primary Entities with Inherited Formal Claims)

## Claim

### Prose Claim

For each Model Entity, group its Property and Relation rules by origin.

- Declared here. The Entity supplies the rule.
- Inherited. A broader Entity supplies the applicable rule.
- Overridden here. The Entity supplies a rule for the same Property or Relation as a broader Entity. Show both rules and their Declaration references.

Distinguish Direct and Derived Relations independently of rule origin. A derived inverse shows the same fact in reverse and retains its Direct Relation and source reference.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Projection


class PrimaryEntitiesWithInheritedFormalClaims(Projection):
    pass


declare_entity(
    entity_class=PrimaryEntitiesWithInheritedFormalClaims,
    entity_name="Primary Entities with Inherited Formal Claims",
    qualification_property_path="Projection.Form",
)
```
