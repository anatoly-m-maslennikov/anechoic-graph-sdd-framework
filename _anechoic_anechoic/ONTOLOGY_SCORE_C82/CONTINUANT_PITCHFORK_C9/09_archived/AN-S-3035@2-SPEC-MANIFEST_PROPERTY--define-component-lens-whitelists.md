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
  version: 2
  updated_at: "2026-11-26T15:54:02.003871+00:00"

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
    property.applies_to = (ComponentManifest,)
    field_options = {'kw_only': True}
    property.cardinality = 1
    property.value.format = list[str]
```
