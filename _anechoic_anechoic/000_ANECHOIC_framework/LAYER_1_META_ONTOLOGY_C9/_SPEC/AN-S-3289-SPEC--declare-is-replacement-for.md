---
atom_family: SPEC
atom_id: AN-S-3289
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: active
  version: 1
  updated_at: '2026-11-21T19:30:00+00:00'
---

## Summary

Declare IS_REPLACEMENT_FOR

## Claim scope

MODEL//ANECHOIC <+ Relation//IS_REPLACEMENT_FOR

## Claim

### Prose Claim

The replacement Atom authors this Relation to a different predecessor Atom
by its stable base Atom ID. One replacement can target several predecessors.
A Draft Host proposes replacement. Its links remain after promotion and
predecessor archival. Completed replacement requires an adopted successor
and an Archived predecessor.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='IS_REPLACEMENT_FOR',
    source_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Atom',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Node//Artifact//Atom',), 'reference_form': 'base_atom_id'},
)
```

## References

AN-S-2733.
