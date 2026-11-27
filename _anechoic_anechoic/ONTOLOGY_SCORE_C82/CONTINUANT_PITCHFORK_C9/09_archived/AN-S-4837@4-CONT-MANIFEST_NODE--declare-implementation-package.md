---
atom_family: SPEC
atom_id: AN-S-4837
concern:
  subject: Implementation Package
  path: Model/Graph/Node//Artifact//SSOT//Realization/Structure/Package
  relation: is_narrower_than
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-26T17:13:49.245990+00:00"
---

## Summary

Declare Implementation Package

## Semantics

A folder with no reserved postfix is an Implementation Package when it contains at least one executable file, directly or in a descendant. Exclude the entire subtree of each descendant folder whose name ends in `__tests`.

Each Implementation Package has exactly one direct executable entry file. Its stem ends in `__shared` or `__public`.

By default, a `__shared` entry is available to the parent and siblings of its Package. An ordered sibling may import it from a lower-layer provider. Apply explicit overrides from the applicable Manifests.

A `__public` entry is available to any importer.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Package

class ImplementationPackage(Package):
    pass
```
