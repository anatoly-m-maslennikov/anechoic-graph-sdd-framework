---
atom_family: SPEC
atom_id: AN-S-3322
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: "archived"
  version: 5
  updated_at: '2026-11-22T22:23:08.810817+00:00'
---

## Summary

Declare CONTRIBUTES_TO

## Claim scope

MODEL//ANECHOIC <+ Relation//CONTRIBUTES_TO

## Claim

### Prose Claim

An Atom contributes when it supplies guidance, design detail, or evidence
that supports a specific claim in the target Atom. In the Contract chain,
a Tier 2 or higher-numbered SPEC Atom contributes to a Tier 1 SPEC Atom
by supporting its design or decision. The authored Relation points from
the contributor to the supported Atom. Derive HAS_CONTRIBUTION for the
same direct pair. The tier rule for this chain is an authoring rule.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='CONTRIBUTES_TO',
    inverse_alias='HAS_CONTRIBUTION',
    source_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Atom//Spec Atom',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Atom//Spec Atom',)},
)
```
