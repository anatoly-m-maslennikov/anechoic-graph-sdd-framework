---
atom_family: SPEC
atom_id: AN-S-2183
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 5
  updated_at: '2026-11-13T01:11:43.332082+00:00'
---
## Summary

Declare Atom.Header

## Claim

### Prose Claim

Atom.Header groups the Atom Properties carried in YAML frontmatter, including for Draft Atoms.

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name="Header",
    relation_name="IS_PROPERTY_OF",
    base_path="Atom",
    property_occurrence_cardinality=1,
    value_cardinality=0,
    dependent_property_cardinality=Cardinality(minimum=0, maximum=None),
    dependent_property_name_format=str,
    allowed_dependent_property_names=("Identity", "Context", "Relations", "State", "Destination"),
    ordered_dependent_property_pairs=(
        ("Identity", "Context"),
        ("Context", "Relations"),
        ("Relations", "State"),
        ("State", "Destination"),
    ),
)
```