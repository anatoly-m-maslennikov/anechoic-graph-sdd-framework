---
atom_id: CA-R-1016
ref_id: CA-R-1016
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Relation//rationale_for
  dependencies:
  - ANECHOIC_MODEL <+ Relation
tier: 1
status: active
version: 34
updated_at: '2026-11-12T12:33:04.158402+00:00'
carrier_destination:
  file:
    name: CA-R-1016-CORE_META_MODEL-DECLARATION--register-rationale-for-relation.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1016-CORE_META_MODEL-DECLARATION--register-rationale-for-relation.md
  source_atom_id: CA-R-1016
  source_atom_revision: 34
  source_sha256: e3085c38a0e3f807e6406ba2ba7091218aecb0fb24ebb34a2c74cfd21e0615dc
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Register rationale_for relation

## Claim

### Prose Claim

#### Applicability
Rationale For Relation.

`rationale_for` **means** the direct relation from a Rationale Analysis and Advisory Atom
to the Atom that it explains.

Forward `Host ((rationale_for)) Target` and reverse `Target <((rationale_for)) Host` are views of the same Relation fact.
rationale_for relates Rationale Analysis and Advisory Atom to explained Atom.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='rationale_for',
    source_endpoint={'level': 'instances',
 'entity_paths': ('Atom/(.Header.Context.Role := Analysis and '
                  'Advisory)/(.Header.Context.Form := Rationale)',)},
    target_endpoint={'level': 'instances', 'entity_paths': ('Atom',)},
)
```

