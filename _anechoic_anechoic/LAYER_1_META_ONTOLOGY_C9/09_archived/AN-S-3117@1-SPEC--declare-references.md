---
atom_family: SPEC
atom_id: AN-S-3117
container:
  component: C9
tier: 2
context:
  lens: SPEC
state:
  status: archived
  version: 1
  updated_at: '2026-11-20T16:37:26.178362+00:00'
---

## Summary

Declare REFERENCES

## Claim scope

MODEL//ANECHOIC <+ Relation//REFERENCES

## Claim

### Prose Claim

The citing Atom records each native Atom target once under `relations.REFERENCES`. A base ID cites the Atom. An exact reference cites a specific Version or Draft. Ownership and replacement follow their declared Relations.

### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name="REFERENCES",
    source_endpoint={"level": "instances", "entity_paths": ("Node//Artifact//Atom",)},
    target_endpoint={"level": "instances", "entity_paths": ("Node//Artifact//Atom",)},
)
```

## Details

- Admit the Relation before authoring citations.
- Verify direct Workbench edges to a base Atom ID and an exact Draft reference.
- Quote the label as `"REFERENCES"` in `GRAPH_TABLE` patterns.
- Resolve legacy citations through an admitted native migration binding.
