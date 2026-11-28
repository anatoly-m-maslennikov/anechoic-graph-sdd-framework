---
atom_family: PROJECT_CONFIG
atom_id: AN-C-3196
concern:
  subject: Template := subject_manifest
  path: Model/Graph/Node//Artifact//SSOT//Prescribed/Content/Atom//Specification//Manifest//.Header.Context
  relation: .
structure:
  container:
    component: C00
context:
  template: manifest_node
state:
  status: archived
  version: 1
  updated_at: "2026-11-27T18:37:10.389486+00:00"
---

## Summary

Declare Subject Manifest Template

## Semantics

A Subject Manifest declares one subject. Its Summary names the subject.
Scope describes the obligations the subject covers. Parent Subject,
when present, names another Subject Manifest by stable Atom ID.
A top-level subject omits Parent Subject. The Container identifies the
owning Component. Subject parentage grants no applicability.

## Formal Manifest

```python anechoic-edsl
# Anechoic Python eDSL

from anechoic.formal_claims import value
from anechoic.model import Component, Lens, Manifest

class SubjectManifest(Manifest):
    node.template = value(fixed='subject_manifest')
    node.tier = value(fixed=2)
    node.lens = value(fixed=Lens.SPEC)
    node.container_type = value(fixed=Component)
```
