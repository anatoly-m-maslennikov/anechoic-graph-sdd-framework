---
atom_family: SPEC
atom_id: AN-S-3320
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: active
  version: 2
  updated_at: '2026-11-22T11:34:35.965837+00:00'
---

## Summary

Declare SERVES

## Claim scope

MODEL//ANECHOIC <+ Relation//SERVES

## Claim

### Prose Claim

A Tier 1 Applicable Principle or Tier 0 Project Contract serves a Project Goal
when part of its purpose is to help achieve that Goal.
The authored Relation points from the stated source to its target.
The inverse is derived. Tier and Solution restrictions are authoring rules.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='SERVES',
    inverse_alias='IS_SERVED_BY',
    source_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Atom//Spec Atom//Applicable Principle', 'Node//Artifact//Atom//Spec Atom//Contract//Project Contract')},
    target_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Atom//Spec Atom//Purpose//Project Goal',)},
)
```
