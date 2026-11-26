---
atom_family: SPEC
atom_id: AN-S-3320
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-22T00:00:00+00:00'
---

## Summary

Declare ADVANCES

## Claim scope

MODEL//ANECHOIC <+ Relation//ADVANCES

## Claim

### Prose Claim

A Tier 1 Applicable Principle or Tier 0 Project Contract advances a Project Goal.
The authored Relation points from the stated source to its target.
The inverse is derived. Tier and Solution restrictions are authoring rules.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='ADVANCES',
    inverse_alias='IS_ADVANCED_BY',
    source_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Atom//Spec Atom//Applicable Principle', 'Node//Artifact//Atom//Spec Atom//Contract//Project Contract')},
    target_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Atom//Spec Atom//Purpose//Project Goal',)},
)
```
