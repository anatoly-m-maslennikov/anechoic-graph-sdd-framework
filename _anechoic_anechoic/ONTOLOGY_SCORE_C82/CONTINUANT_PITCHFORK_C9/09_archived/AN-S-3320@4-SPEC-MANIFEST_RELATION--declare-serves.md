---
atom_family: SPEC
atom_id: AN-S-3320
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-26T15:54:02.694435+00:00"
---

## Summary

Declare SERVES

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//SERVES

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
