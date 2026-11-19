---
atom_id: CA-R-2456
ref_id: CA-R-2456
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Carrier/File/Markdown
  dependencies:
  - ANECHOIC_MODEL <+ Carrier/File
tier: 1
status: active
version: 6
updated_at: '2026-11-12T17:23:54+00:00'
carrier_destination:
  file:
    name: CA-R-2456-CORE_META_MODEL-DECLARATION--define-markdown-file-carrier.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2456-CORE_META_MODEL-DECLARATION--define-markdown-file-carrier.md
  source_atom_id: CA-R-2456
  source_atom_revision: 6
  source_sha256: 45295083d79adf440ac7e1748720290bc062fce38552aee9c861280657d0260a
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Define Markdown File Carrier

## Claim

### Prose Claim

A Markdown File Carrier is a File Carrier represented using Markdown.
### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import File

class Markdown(File):
    pass

declare_entity(entity_class=Markdown, entity_name='Markdown')
```

