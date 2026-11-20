---
atom_family: SPEC
atom_id: AN-S-2716
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 9
  updated_at: '2026-11-13T00:36:29.288696+00:00'
---
## Summary

Define HAS_INVERSE

## Claim

### Prose Claim

HAS_INVERSE binds a canonical Relation to its reverse alias. The canonical Declaration defines the shared meaning, endpoint constraints, and alias. The reverse view follows from the same graph fact. It swaps the endpoints and their cardinality slots and retains any declared qualification.

`<-->` writes this binding in a Subject. `Relation//DIRECT <--> Relation//REVERSE` names the canonical Relation on the left and its reverse alias on the right. Each direction keeps its own admitted permissions and bounds.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='HAS_INVERSE',
    source_endpoint={'level': 'model_entities', 'entity_paths': ('Relation',), 'address_form': 'canonical'},
    target_endpoint={'level': 'model_entities', 'entity_paths': ('Relation',), 'address_form': 'inverse_alias'},
    written_alias='<-->',
)
```
