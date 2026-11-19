---
atom_id: CA-R-1660
ref_id: CA-R-1660
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Relation//structural_parent
  dependencies:
  - ANECHOIC_MODEL <+ Scope Unit
tier: 1
status: active
version: 38
updated_at: '2026-11-12T20:21:10.600815+00:00'
carrier_destination:
  file:
    name: CA-R-1660-CORE_META_MODEL-DECLARATION--register-structural-parent-relation.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1660-CORE_META_MODEL-DECLARATION--register-structural-parent-relation.md
  source_atom_id: CA-R-1660
  source_atom_revision: 38
  source_sha256: 0399f43db9ebffdacc020796777a50186a21d959c6f7805908a36156263ba611
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Register structural parent relation

## Claim

### Prose Claim

#### Applicability
the Structural Parent Relation directed from a child to its immediate parent.

the Structural Parent Relation **must** be the kind-independent Structural ownership relation directed from a child **to** its immediate parent. Project Structure owns Scope Unit parent declarations; structural graph views derive the corresponding `structural_parent` edge **without** maintaining a second source. a Carrier's physical containment **must not** silently replace a declared logical parent.

The Host is a structural child and the Target is its immediate structural parent.
Forward `Host ((structural_parent)) Target` and reverse `Target <((structural_parent)) Host` are views of the same Relation fact.
structural_parent relates structural child to immediate structural parent.
### Formal Claim

```python
from anechoic.formal_claims import declare_relation

declare_relation(
    relation_name='structural_parent',
    source_endpoint={'level': 'instances'},
    target_endpoint={'level': 'instances'},
)
```

