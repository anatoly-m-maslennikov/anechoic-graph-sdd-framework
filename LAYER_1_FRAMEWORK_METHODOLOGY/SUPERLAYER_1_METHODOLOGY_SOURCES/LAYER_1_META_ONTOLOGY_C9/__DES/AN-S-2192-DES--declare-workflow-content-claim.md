---
atom_family: SPEC
atom_id: AN-S-2192
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-13T03:15:59.506677+00:00'
---

## Summary

Declare Workflow.Content.Claim

## Claim

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name="Claim",
    relation_name="IS_PROPERTY_OF",
    base_path="Workflow.Content",
    property_occurrence_cardinality=1,
    value_cardinality=0,
    dependent_property_cardinality=Cardinality(minimum=1, maximum=3),
    allowed_dependent_property_names=("Mermaid Scheme", "Prose Claim", "Formal Claim"),
    ordered_dependent_property_pairs=(
        ("Mermaid Scheme", "Prose Claim"),
        ("Prose Claim", "Formal Claim"),
    ),
)
```

## Semantics

Workflow Claim has unique child Property names. At least one of Prose Claim and Formal Claim is present, and their text together specifies the Workflow completely without reliance on the Mermaid Scheme.
