---
atom_family: SPEC
atom_id: AN-S-4896
concern:
  subject: Lens
  path: Model/Graph
  relation: is_contained_by
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: archived
  version: 6
  updated_at: "2026-11-27T18:25:19.395007+00:00"
---

## Summary

Declare Lens

## Semantics

A Lens groups Spec Atoms by the concern they address. Each Lens has one
canonical Manifest with its meaning, axis presets, and sources. A narrower
Lens specializes its parent's scope.

A Lens can list canonical sublenses and links to Lenses already declared
elsewhere in the tree. A link exposes the target in another grouping.
Each alternative lists the subparts that make up one grouping.

`BACKEND = API + SWE` illustrates another grouping. SYS and BACKEND share
SWE. Each also covers paths the other omits, so they can serve different
Components.

`IO = API + UI`. `API = CLI + REST API + DTA + MCP + IPC` groups programmatic
interfaces. `UI = UX + VIS` groups user experience and visual design.

Each Component selects the Lens scopes for its own Spec Atoms. A Spec Atom
uses one authored Lens path. Within a Component, expanded scopes can be
disjoint or nested. Partial overlap is invalid.

A fixed preset must hold. An authored value can override a default. Project
and Component Manifests select the Lens paths they enable.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import SpecificationLens

class Lens:
    node.parts = {
        'SPEC': SpecificationLens,
    }
```

## Sources

- [ISO/IEC/IEEE 42010:2022 — Architecture description](https://www.iso.org/standard/74393.html) covers architecture viewpoints and concerns.
