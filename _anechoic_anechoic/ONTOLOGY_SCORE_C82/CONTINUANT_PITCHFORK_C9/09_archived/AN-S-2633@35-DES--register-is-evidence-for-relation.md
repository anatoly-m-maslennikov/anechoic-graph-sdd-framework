---
atom_family: SPEC
atom_id: AN-S-2633
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 35
  updated_at: "2026-11-26T11:51:52.779908+00:00"
---

## Summary

Register IS_EVIDENCE_FOR relation

## Claim

### Prose Claim

IS_EVIDENCE_FOR is the direct Relation owned by an evidence Carrier. The Host is that evidence Carrier and each tuple targets the Evaluation or Implementation Carrier it supports.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='IS_EVIDENCE_FOR',
    source_endpoint={'level': 'instances', 'entity_paths': ('Carrier',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Carrier',)},
)
```
