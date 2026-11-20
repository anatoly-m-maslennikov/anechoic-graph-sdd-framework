---
identity:
  atom_id: AN-S-3117
context:
  container:
    component: C9
  lens: SPEC
state:
  status: draft
  version: 1
  updated_at: '2026-11-20T14:13:02.133321+00:00'
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

Admit the Relation to the native Model before authoring citations that use it. Verify that Workbench publishes direct edges to a base Atom ID and an exact Draft reference. Resolve legacy citations through an admitted native migration binding.
