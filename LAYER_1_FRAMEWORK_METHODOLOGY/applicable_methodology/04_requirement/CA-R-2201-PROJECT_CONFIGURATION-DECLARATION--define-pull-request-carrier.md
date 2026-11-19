---
atom_id: CA-R-2201
ref_id: CA-R-2201
container:
  scope_unit: CA-SU-13
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Carrier/Pull Request
tier: 1
status: active
version: 8
updated_at: '2026-11-12T17:23:54+00:00'
carrier_destination:
  file:
    name: CA-R-2201-PROJECT_CONFIGURATION-DECLARATION--define-pull-request-carrier.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/04_requirement/CA-R-2201-PROJECT_CONFIGURATION-DECLARATION--define-pull-request-carrier.md
  source_atom_id: CA-R-2201
  source_atom_revision: 8
  source_sha256: daa8a20f03f0c39197640cd47c441e2beb58d18e649f97a6933df7fd8567e44d
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Define Pull Request Carrier

## Claim

### Prose Claim

A Pull Request is a repository-hosted Carrier of a proposed change and its review state.
### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Carrier

class PullRequest(Carrier):
    pass

declare_entity(entity_class=PullRequest, entity_name='Pull Request')
```

