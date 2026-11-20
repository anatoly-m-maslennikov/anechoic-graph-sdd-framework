---
atom_family: SPEC
atom_id: AN-S-2633
structure:
  container:
    component: C9
  tier: 1
context:
  lens: DES
state:
  status: active
  version: 34
  updated_at: '2026-11-12T23:18:16.780674+00:00'
---

## Summary

Register evidence_for relation

## Claim

### Prose Claim

evidence_for is the direct Relation owned by an evidence Carrier. The Host is that evidence Carrier and each tuple targets the Evaluation or Implementation Carrier it supports.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='evidence_for',
    source_endpoint={'level': 'instances', 'entity_paths': ('Carrier',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Carrier',)},
)
```

