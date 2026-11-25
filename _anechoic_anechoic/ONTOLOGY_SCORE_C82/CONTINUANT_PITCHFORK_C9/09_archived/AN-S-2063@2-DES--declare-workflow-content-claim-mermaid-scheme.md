---
atom_family: SPEC
atom_id: AN-S-2063
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-25T23:01:32.998331+00:00"
---

## Summary

Declare Workflow.Content.Claim.Mermaid Scheme

## Claim

### Prose Claim

The scheme shows all Workflow Steps, including nested Steps.

### Formal Claim

```python
# model
from anechoic.formal_claims import declare_entity

declare_entity(
    entity_name='Mermaid Scheme',
    relation_name='IS_PROPERTY_OF',
    base_path='Workflow.Content.Claim',
    property_occurrence_cardinality=1,
    value_cardinality=1,
    value_format='markdown',
    dependent_property_cardinality=0,
)
```

## Semantics

The value is exactly one `mermaid`-labelled fenced Markdown block. A Mermaid Scheme is a visual Minto summary of its owning Claim's text: removing it must leave that text's specification complete and unchanged. It may repeat the text.
