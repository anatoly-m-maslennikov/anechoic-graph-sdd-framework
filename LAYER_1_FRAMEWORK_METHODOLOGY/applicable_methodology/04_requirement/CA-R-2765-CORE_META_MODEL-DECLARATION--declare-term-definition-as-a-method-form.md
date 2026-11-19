---
atom_id: CA-R-2765
ref_id: CA-R-2765
container:
  scope_unit: CA-SU-11
role: Requirement
form: Declaration
topics:
  main_subject: ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Method)/(.Header.Context.Form
    := Term Definition)
  dependencies:
  - ANECHOIC_MODEL <+ Atom/(.Header.Context.Role := Method)
tier: 3
status: active
version: 7
updated_at: '2026-11-12T17:23:54+00:00'
carrier_destination:
  file:
    name: CA-R-2765-CORE_META_MODEL-DECLARATION--declare-term-definition-as-a-method-form.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-2765-CORE_META_MODEL-DECLARATION--declare-term-definition-as-a-method-form.md
  source_atom_id: CA-R-2765
  source_atom_revision: 7
  source_sha256: 593605b7dbe90ed718a43a2f67058044227eb64681de50e83916fd601d37341a
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
## Summary

Declare Term Definition as a Method Form

## Claim

### Formal Claim

```python
from anechoic.formal_claims import declare_entity
from anechoic.model import Method

class TermDefinition(Method):
    pass

declare_entity(entity_class=TermDefinition, entity_name='Term Definition', qualification_property_path="Atom.Header.Context.Form")
```
