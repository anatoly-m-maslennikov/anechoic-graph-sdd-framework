---
atom_id: CA-R-2955
ref_id: CA-R-2955
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Requirement)/(.Header.Context.Form
    := Relation Declaration)
  dependencies:
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Requirement)
tier: 3
status: active
version: 3
updated_at: '2026-11-12T17:23:54+00:00'
carrier_destination:
  file:
    name: CA-R-2955-CORE_META_MODEL-DECLARATION--declare-relation-declaration-as-a-requirement-form.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2955-CORE_META_MODEL-DECLARATION--declare-relation-declaration-as-a-requirement-form.md
  source_atom_id: CA-R-2955
  source_atom_revision: 3
  source_sha256: 97e3d287790c2ae017de1fe42f578f2fce4287fb44a20afe1c13ee9ba52a1db2
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---

## Summary

Declare Relation Declaration as a Requirement Form

## Claim

### Prose Claim

This Form uses the Declaration contract.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Requirement

class RelationDeclaration(Requirement):
    pass

declare_entity(entity_class=RelationDeclaration, entity_name='Relation Declaration', qualification_property_path="Atom.Header.Context.Form")
```

## Semantics

A Relation Declaration defines a canonical binary Relation, its endpoint domains and applicable inverse aliases.
