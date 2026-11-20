---
atom_family: SPEC
atom_id: AN-S-2185
structure:
  container:
    component: C9
  tier: 1
context:
  lens: DevOps
state:
  status: active
  version: 6
  updated_at: '2026-11-13T01:58:33.789950+00:00'
---


## Summary

Derive Authority and Delivery Folder Names

## Claim

### Prose Claim


The Project’s `Scope Unit.Paths.Authority` is `.anechoic_<project name>`. Its `Scope Unit.Paths.Delivery` is `.`, the Project root.

For a non-root Scope Unit, derive the folder names from its ID, Label, order.number and Name:

| Scope Unit | Authority Folder name | Delivery Folder name |
| --- | --- | --- |
| Ordered | `<id>_<label>_<order>_<name>` | `<label>_<order>_<name>` |
| Unordered | `<id>_<label>_<name>` | `<label>_<name>` |

`<id>` is the stable Scope Unit ID. `<order>` is `order.number`. For an Unordered unit, omit the order segment and its separator. When Label is absent, omit its segment and separator.

Place each non-root folder under its respective parent's folder. Resolve `Scope Unit.Paths.Authority` and `Scope Unit.Paths.Delivery` from their respective folder trees relative to the Project root. Do not maintain the derived folder paths as independent values in Scope Unit Declarations.

Derived paths are readability and placement values, not another structural source. Conflicting derivations remain unresolved and are reported; do not automatically choose a new Name, parent, number or binding. Do not author Structural Coordinate.
