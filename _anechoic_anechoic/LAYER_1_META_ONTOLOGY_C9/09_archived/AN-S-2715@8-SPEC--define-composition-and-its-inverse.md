---
atom_family: SPEC
atom_id: AN-S-2715
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: archived
  version: 8
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Define composition and its inverse

## Claim scope

MODEL//ANECHOIC <+ Relation//CONTAINED_BY

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name="CONTAINED_BY",
    inverse_alias="CONTAINS",
    reverse_written_alias="<+",
    endpoint_pairs=(
        {
            "source_endpoint": {"level": "model_entities", "entity_paths": ("Graph", "eDSL", "Carrier")},
            "target_endpoint": {"level": "model_entities", "entity_paths": ("Model",)},
        },
        {
            "source_endpoint": {"level": "model_entities", "entity_paths": ("Node", "Relation")},
            "target_endpoint": {"level": "model_entities", "entity_paths": ("Graph",)},
        },
        {
            "source_endpoint": {"level": "model_entities", "entity_paths": ("Format", "Cardinality")},
            "target_endpoint": {"level": "model_entities", "entity_paths": ("eDSL",)},
        },
        {
            "source_endpoint": {"entity_paths": ("Component Spec Section", "Node//Artifact//Package//Component Package")},
            "target_endpoint": {"entity_paths": ("Node//Artifact//Component",)},
        },
        {
            "source_endpoint": {"entity_paths": ("Node//Artifact//Package", "Module")},
            "target_endpoint": {"entity_paths": ("Node//Artifact//Package",)},
        },
        {
            "source_endpoint": {"entity_paths": ("Unit",)},
            "target_endpoint": {"entity_paths": ("Module",)},
        },
        {
            "source_endpoint": {"level": "instances", "entity_paths": ("Node//Artifact//Atom",)},
            "target_endpoint": {"level": "instances", "entity_paths": ("Node//Artifact//Component", "Node//Artifact//Atom")},
        },
    ),
)
```
