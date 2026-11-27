---
atom_family: SPEC
atom_id: AN-S-3320
concern:
  subject: SERVES
  path: Model/Graph/Relation
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_relation
  lens: DOM/CONT
state:
  status: "active"
  version: 5
  updated_at: "2026-11-26T15:52:34.611977+00:00"
---

## Summary

Declare SERVES

## Claim

### Prose Claim

A Tier 1 Applicable Principle or Tier 0 Project Contract serves a Project Goal
when part of its purpose is to help achieve that Goal.
The authored Relation points from the stated source to its target.
The inverse is derived. Tier and Solution restrictions are authoring rules.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ApplicablePrinciple, ProjectContract, ProjectGoal, Relation

class Relation3320(Relation):
    name = 'SERVES'
    relation.inverse_alias = 'IS_SERVED_BY'
    relation.source_endpoint = {'level': 'instances', 'entity_paths': (ApplicablePrinciple, ProjectContract)}
    relation.target_endpoint = {'level': 'instances', 'entity_paths': (ProjectGoal,)}
```
