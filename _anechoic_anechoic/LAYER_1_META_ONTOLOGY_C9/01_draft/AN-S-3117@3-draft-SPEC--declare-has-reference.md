---
atom_family: SPEC
atom_id: AN-S-3117
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: draft
  version: 3
  updated_at: '2026-11-21T13:03:17+00:00'
---

## Summary

Declare HAS_REFERENCE

## Claim scope

MODEL//ANECHOIC <+ Relation//HAS_REFERENCE

## Claim

### Prose Claim

The citing Atom records each native Atom target once under `relations.HAS_REFERENCE`. A base ID cites the Atom. An exact reference cites a specific Version or Draft. Ownership and replacement follow their declared Relations.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name="HAS_REFERENCE",
    source_endpoint={"level": "instances", "entity_paths": ("Node//Artifact//Atom",)},
    target_endpoint={"level": "instances", "entity_paths": ("Node//Artifact//Atom",)},
    inverse_alias="IS_REFERENCE_FOR",
    classifications={"Transitive": "no", "Functional": "no"},
    inverse_classifications={"Transitive": "no", "Functional": "no"},
)
```

## Details

- Admit the Relation before authoring citations.
- Verify direct Workbench edges to a base Atom ID and an exact Draft reference.
- Quote the label as `"HAS_REFERENCE"` in `GRAPH_TABLE` patterns.
- Resolve legacy citations through an admitted native migration binding.

## Direction

A citing Atom has a reference to the cited Atom. Derive IS_REFERENCE_FOR
by reversing one authored fact. Preserve existing REFERENCES targets
when reading historical Carriers.
