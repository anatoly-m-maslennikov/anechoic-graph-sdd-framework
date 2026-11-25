---
atom_family: SPEC
atom_id: AN-S-2727
container:
  component: C9
tier: 1
context:
  lens: SPEC
state:
  status: draft
  version: 5
  updated_at: '2026-11-21T13:03:17+00:00'
---
## Summary

Declare SPECIALIZES

## Claim scope

MODEL//ANECHOIC <+ Relation//SPECIALIZES

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name="SPECIALIZES",
    source_endpoint={"level": "instances", "entity_paths": ("Node//Artifact//Atom",)},
    target_endpoint={"level": "instances", "entity_paths": ("Node//Artifact//Atom",)},
    inverse_alias="IS_SPECIALIZED_BY",
    classifications={"Transitive": "no", "Functional": "no"},
    inverse_classifications={"Transitive": "no", "Functional": "no"},
)
```

## Semantics

SPECIALIZES relates a child Atom to the Atom whose Claim it specializes.

## Migration authority

CA-R-2766 and AN-T-2800.
