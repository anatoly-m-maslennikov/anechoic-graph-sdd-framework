---
atom_family: SPEC
atom_id: AN-S-2714
structure:
  container:
    component: C9
context:
  lens: SPEC
state:
  status: active
  version: 7
  updated_at: '2026-11-20T11:17:59+00:00'
---

## Summary

Define classification and its written reverse

## Claim scope

MODEL//ANECHOIC <+ Relation//IS_CLASSIFIED_BY

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name="IS_CLASSIFIED_BY",
    inverse_alias="CLASSIFIES",
    endpoint_pairs=(
        {
            "source_endpoint": {"level": "model_entities", "entity_paths": ("Node//Artifact//Atom//Spec Atom", "Node//Artifact//Atom//PMETA Atom")},
            "target_endpoint": {"level": "model_entities", "entity_paths": ("Continuant",)},
        },
        {
            "source_endpoint": {"level": "model_entities", "entity_paths": ("Node//Artifact//Atom//Ticket Atom",)},
            "target_endpoint": {"level": "model_entities", "entity_paths": ("Occurrent",)},
        },
        {
            "source_endpoint": {"level": "model_entities", "entity_paths": ("Node//Artifact//Atom//Spec Atom", "Node//Artifact//Event Record")},
            "target_endpoint": {"level": "model_entities", "entity_paths": ("SSOT",)},
        },
    ),
)
```
