---
atom_family: SPEC
atom_id: AN-S-4837
container:
  component: C9
tier: 2
context:
  lens: SPEC
  template: manifest_node
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-25T19:42:27.279057+00:00"
---

## Summary

Declare Implementation Package

## Claim scope

MODEL//ANECHOIC <+ Graph/Node//Artifact//SSOT//Realization/Structure/Package//Implementation Package

## Semantics

An Implementation Package has no reserved postfix. It has exactly one direct executable entry file. The file stem ends in `__shared` or `__public`.

By default, a `__shared` entry is available to the parent and siblings of its Package. An ordered sibling may import it from a lower-layer provider. Apply explicit overrides from the applicable Manifests.

A `__public` entry is available to any importer.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.model import Package

class ImplementationPackage(Package):
    pass
```
