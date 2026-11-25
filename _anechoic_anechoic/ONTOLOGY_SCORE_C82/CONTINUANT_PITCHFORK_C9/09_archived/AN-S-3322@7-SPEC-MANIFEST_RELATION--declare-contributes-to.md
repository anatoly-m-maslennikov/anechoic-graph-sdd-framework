---
atom_family: SPEC
atom_id: AN-S-3322
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_relation
state:
  status: "archived"
  version: 7
  updated_at: "2026-11-25T19:32:43.296825+00:00"
---

## Summary

Declare CONTRIBUTES_TO

## Claim scope

MODEL//ANECHOIC <+ Graph/Relation//CONTRIBUTES_TO

## Claim

### Prose Claim

An Atom contributes when it supplies guidance, design detail, or evidence
that supports a specific claim in the target Atom. In the Contract chain,
a Tier 2 or higher-numbered SPEC Atom contributes to a Tier 1 SPEC Atom
by supporting its design or decision. The authored Relation points from
the contributor to the supported Atom. Derive HAS_CONTRIBUTION for the
same direct pair. The tier rule for this chain is an authoring rule.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Relation, SpecAtom

class Relation3322(Relation):
    name = 'CONTRIBUTES_TO'
    relation.inverse_alias = 'HAS_CONTRIBUTION'
    relation.source_endpoint = {'level': 'instances', 'entity_paths': (SpecAtom,)}
    relation.target_endpoint = {'level': 'instances', 'entity_paths': (SpecAtom,)}
```
