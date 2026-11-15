---
atom_id: CA-R-1199
ref_id: CA-R-1199
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: CAPRMEDIO_MODEL <+ Relation//GOVERNS
  dependencies:
  - CAPRMEDIO_MODEL <+ Relation
  - CAPRMEDIO_MODEL <+ Atom
  - CAPRMEDIO_MODEL <+ Entity
  - CAPRMEDIO_MODEL <+ Atom.Content
  - CAPRMEDIO_MODEL <+ Atom.Header.Context.Topics
tier: 2
status: active
version: 39
updated_at: '2026-11-12T17:23:54+00:00'
carrier_destination:
  file:
    name: CA-R-1199-CORE_META_MODEL-DECLARATION--define-governs-subject-relation-kind.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-1199-CORE_META_MODEL-DECLARATION--define-governs-subject-relation-kind.md
  source_atom_id: CA-R-1199
  source_atom_revision: 39
  source_sha256: 87916ade0f1498c8464e2f868c3d407f5e6f7f10d0903955df6c3734d5fab034
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Define GOVERNS Subject Relation Kind

## Claim

### Prose Claim

#### Applicability
the GOVERNS Subject Relation Kind.

GOVERNS **means** the direct Subject Relation Kind from an Atom **to** the canonical Subject entity or instance about which the Atom governs through its applicable role-specific content.

The Target is the canonical Subject about which the Atom governs through its applicable content.
Forward `Host ((GOVERNS)) Target` and reverse `Target <((GOVERNS)) Host` are views of the same Relation fact.
GOVERNS relates Atom to canonical Subject entity or instance.
### Formal Claim

```python
from caprmedio.formal_claims import declare_relation

declare_relation(
    relation_name='GOVERNS',
    source_endpoint={'level': 'instances', 'entity_paths': ('Atom',)},
    target_endpoint={'level': 'model_entities_or_instances'},
)
```

