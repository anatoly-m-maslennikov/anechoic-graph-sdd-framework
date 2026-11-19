---
atom_id: CA-R-1022
ref_id: CA-R-1022
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Relation//concern_about
  dependencies:
  - ANECHOIC_MODEL <+ Relation
tier: 1
status: active
version: 33
updated_at: '2026-11-12T20:24:07.873527+00:00'
carrier_destination:
  file:
    name: CA-R-1022-CORE_META_MODEL-DECLARATION--register-concern-about-relation.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1022-CORE_META_MODEL-DECLARATION--register-concern-about-relation.md
  source_atom_id: CA-R-1022
  source_atom_revision: 33
  source_sha256: ef32a9fea5941c6ebcc3b2bc59cef11e7e1d6c8ef7304cc15607a91b3aa3e3d4
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Register concern_about relation

## Claim

### Prose Claim

#### Applicability
`concern_about` relations.

`concern_about` **means** the direct relation from a Concern Atom to the
governed entity that it concerns.

The Host is a Concern Atom; the governed target is the Entity concerned.
Forward `Host ((concern_about)) Target` and reverse `Target <((concern_about)) Host` are views of the same Relation fact.
concern_about relates Concern Atom to governed entity concerned.

#### Details
Endpoint admission is an Atom Entity Definition concern, not Relation Definition
metadata.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='concern_about',
    source_endpoint={'level': 'instances', 'entity_paths': ('Atom/(.Header.Context.Role:=Concern)',)},
    target_endpoint={'level': 'model_entities_or_instances'},
)
```

