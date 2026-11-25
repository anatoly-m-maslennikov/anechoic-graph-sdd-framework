---
atom_family: SPEC
atom_id: AN-S-2712
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: active
  version: 8
  updated_at: '2026-11-13T22:36:02.766934+00:00'
---
## Summary

Define NARROWER_THAN

## Claim

### Prose Claim

NARROWER_THAN relates a narrower MODEL kind to a broader MODEL kind. A Property does not narrow. Both endpoints are MODEL kinds; Property bearers and instance populations do not become kinds through this notation. The narrower kind inherits applicable Relation and Property constraints without cloning declarations or instance facts. HAS_NARROWER is its derived inverse. In `X/Y`, Y is narrower than X; traversal runs from broader to narrower.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='NARROWER_THAN',
    source_endpoint={'level': 'model_entities'},
    target_endpoint={'level': 'model_entities'},
    inverse_alias='HAS_NARROWER',
    reverse_written_alias='/',
)
```

