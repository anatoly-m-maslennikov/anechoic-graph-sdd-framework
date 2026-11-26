---
atom_family: SPEC
atom_id: AN-S-3035
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_property
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-25T12:40:53.755977+00:00"
relations:
  IS_REFERENCE:
  - AN-S-4896@1
---

## Summary

Define Component lens whitelists

## Semantics

Each Component Manifest declares the Lenses or named groups allowed for its
own Spec Atoms. An empty list allows none.

Expand each entry to its canonical Lens paths. For each pair, the sets must
be disjoint or one must contain the other. Reject partial overlap.
Different Components can choose different lists.

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest//Component Manifest.Lens Whitelist

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import ComponentManifest, Manifest, Property

class ComponentLensWhitelist(Property):
    name = 'Lens Whitelist'
    bearer = Manifest
    applies_to_entity_classes = (ComponentManifest,)
    field_options = {'kw_only': True}
    property_occurrence_cardinality = 1
    value_format = list[str]
```
