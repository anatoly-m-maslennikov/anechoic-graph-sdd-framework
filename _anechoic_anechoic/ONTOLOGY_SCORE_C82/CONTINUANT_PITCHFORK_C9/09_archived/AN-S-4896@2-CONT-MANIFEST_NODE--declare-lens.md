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
  status: "archived"
  version: 2
  updated_at: "2026-11-26T16:50:19.118076+00:00"
---

## Summary

Declare Lens

## Semantics

A Lens groups Spec Atoms by the concern they address. Its full path identifies it
in the Lens tree. A sublens uses its parent's path as a prefix.

Each Component selects the Lens scopes for its own Spec Atoms. A Spec Atom
uses one authored Lens path. Within a Component, expanded scopes can be
disjoint or nested. Partial overlap is invalid.

The Lens tree can supply alternative subtrees. Named groups can combine
Lens paths and other groups. Group definitions may share members.

`DOM = ONT + MTD`. The sublenses use paths `DOM/ONT` and `DOM/MTD`.

For example, SPEC can cover DOM and SWE. A Component can select SPEC, DOM,
and SWE together, as well as DEVOPS, QA, and SWD within SWE.

`DES = IO + DOM`, `SWE = SWD + QA + DEVOPS`, `SYS = SWE + DOM`, and
`BACKEND = API + SWE` illustrate possible groupings. SYS and BACKEND share
SWE. Each also covers paths the other omits, so they can serve different
Components.

`IO = API + UI`. `API = CLI + REST API + DTA + MCP` groups programmatic
interfaces. `UI = UX + VIS` groups user experience and visual design.

Each Lens has one Manifest with its meaning, axis presets, and sources. A fixed
preset must hold. An authored value can override a default. Project and Component
Manifests select the Lens paths they enable.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

class Lens:
    pass
```
