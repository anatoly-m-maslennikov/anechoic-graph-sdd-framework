---
atom_id: CA-R-2457
ref_id: CA-R-2457
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Carrier/File/Markdown/Markdown Atom Carrier
  dependencies:
  - ANECHOIC_MODEL <+ Carrier/File/Markdown
  - ANECHOIC_MODEL <+ Atom
  - ANECHOIC_MODEL <+ Carrier/File
tier: 1
status: active
version: 6
updated_at: '2026-11-12T17:23:54+00:00'
carrier_destination:
  file:
    name: CA-R-2457-CORE_META_MODEL-DECLARATION--define-markdown-atom-carrier.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
current_scope_unit: CORE_META_MODEL
claim_target_scope_unit: CORE_META_MODEL
---
## Summary

Define Markdown Atom Carrier

## Claim

### Prose Claim

A Markdown Atom Carrier is a Markdown File Carrier that represents an Atom.
### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Markdown

class MarkdownAtomCarrier(Markdown):
    pass

declare_entity(entity_class=MarkdownAtomCarrier, entity_name='Markdown Atom Carrier')
```

