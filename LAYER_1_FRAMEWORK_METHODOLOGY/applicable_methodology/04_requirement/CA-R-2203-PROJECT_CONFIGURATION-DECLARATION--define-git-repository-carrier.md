---
atom_id: CA-R-2203
ref_id: CA-R-2203
container:
  scope_unit: CA-SU-13
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Carrier/Git Repository
tier: 1
status: active
version: 9
updated_at: '2026-11-12T17:23:54+00:00'
carrier_destination:
  file:
    name: CA-R-2203-PROJECT_CONFIGURATION-DECLARATION--define-git-repository-carrier.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement/CA-R-2203-PROJECT_CONFIGURATION-DECLARATION--define-git-repository-carrier.md
  source_atom_id: CA-R-2203
  source_atom_revision: 9
  source_sha256: be06f56a8577e0b122a00de8153b6cab462179b5c0973c3e0aac219d16a6d4b2
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Define Git Repository Carrier

## Claim

### Prose Claim

A Git Repository is a Carrier of versioned content and Git references.

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Carrier

class GitRepository(Carrier):
    pass

declare_entity(entity_class=GitRepository, entity_name='Git Repository')
```

## Semantics

Git Repository contains Git Branches; this is containment, not specialization.
