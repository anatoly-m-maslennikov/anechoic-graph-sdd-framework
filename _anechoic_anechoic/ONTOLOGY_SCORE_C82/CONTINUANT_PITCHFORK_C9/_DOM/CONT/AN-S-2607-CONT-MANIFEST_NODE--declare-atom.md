---
atom_family: SPEC
atom_id: AN-S-2607
concern:
  subject: Atom
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content
  relation: is_contained_by
container:
  component: C9
tier: 2
context:
  template: manifest_node
  lens: DOM/CONT
state:
  status: "active"
  version: 24
  updated_at: "2026-11-26T14:46:18.727895+00:00"
---

## Summary

Declare Atom

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import MarkdownWithYAMLFrontMatter, Prescribed

class Atom(Prescribed):
    node.identity = header.atom_id
    node.ssot_carrier = value(fixed=MarkdownWithYAMLFrontMatter)
```

## Semantics

The authoritative Markdown file stores the Atom revision’s YAML Header and Markdown Content. Use the actual Carrier path and filename to locate that revision. Header.Container determines its containment. Carry the applicable authored properties on the Atom. Resolve other Atoms and governing declarations by reference.

Each contained Atom has its own identity and lifecycle. A change confined to the contained Atoms preserves the containing Atom’s identity.

Derive the expected Carrier filename and path from the Header and Content Summary using the declared Project Structure. A different filename or path is a placement discrepancy.
