---
atom_family: SPEC
atom_id: AN-S-3117
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: active
  version: 3
  updated_at: '2026-11-21T19:14:35.061068+00:00'
---

## Summary

Declare IS_REFERENCE

## Claim scope

MODEL//ANECHOIC <+ Relation//IS_REFERENCE

## Claim

### Prose Claim

The citing Atom records each native Atom target once under `relations.IS_REFERENCE`. A base ID cites the Atom. An exact reference cites a specific Version or Draft. Ownership and replacement follow their declared Relations.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name="IS_REFERENCE",
    inverse_alias="HAS_REFERENCE",
    source_endpoint={"level": "instances", "entity_paths": ("Node//Artifact//Atom",)},
    target_endpoint={"level": "instances", "entity_paths": ("Node//Artifact//Atom",)},
)
```

## Details

- Admit the Relation before authoring citations.
- Verify direct Workbench edges to a base Atom ID and an exact Draft reference.
- Quote the label as `"IS_REFERENCE"` in `GRAPH_TABLE` patterns.
- Resolve legacy citations through an admitted native migration binding.

## Classifications

| Relation | Transitive | Functional |
| --- | --- | --- |
| `IS_REFERENCE` | no | no |

An Atom can cite several targets. Each edge records a citation by its source Atom.

The citing Atom authors `IS_REFERENCE`; derive `HAS_REFERENCE` by reversing
the edge. Preserve target and direction when migrating `REFERENCES`.
