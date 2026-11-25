---
atom_family: SPEC
atom_id: AN-S-3362
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-22T22:23:08.810817+00:00'
---

## Summary

Declare ANSWERS

## Claim scope

MODEL//ANECHOIC <+ Relation//ANSWERS

## Claim

### Prose Claim

A Tier 0 Contract answers a Manifest by accepting a specific responsibility
the Manifest assigns. The Contract states what the Component commits to
deliver and what it requires from callers. The authored Relation points from
the Contract to the Manifest. Derive IS_ANSWERED_BY for the same direct pair.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='ANSWERS',
    inverse_alias='IS_ANSWERED_BY',
    source_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Atom//Spec Atom//Contract',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Atom//Spec Atom//Manifest',)},
)
```
