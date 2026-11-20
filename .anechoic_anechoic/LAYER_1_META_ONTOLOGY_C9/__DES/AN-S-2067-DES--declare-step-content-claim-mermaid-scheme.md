---
atom_family: SPEC
atom_id: AN-S-2067
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: '2026-11-12T18:39:04.030100+00:00'
---

## Summary

Declare Step.Content.Claim.Mermaid Scheme

## Claim

### Prose Claim

Mermaid Scheme semantics: [Workflow Mermaid Scheme declaration](CA-R-2962-CORE_META_MODEL-DECLARATION--declare-workflow-content-claim-mermaid-scheme.md#semantics).

### Formal Claim

```python
from anechoic.formal_claims import Cardinality, declare_entity

declare_entity(
    entity_name="Mermaid Scheme",
    relation_name="IS_PROPERTY_OF",
    base_path='Atom/(.Header.Context.Role := Operations)/(.Header.Context.Form := Step).Content.Claim',
    property_occurrence_cardinality=Cardinality(minimum=0, maximum=1),
    value_format="markdown",
    value_cardinality=1,
    dependent_property_cardinality=0,
)
```
