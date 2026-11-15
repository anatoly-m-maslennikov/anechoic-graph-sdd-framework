---
identity:
  id: CA-R-3075
  ref_id: CA-R-3075
context:
  container:
    scope_unit: CA-SU-11
  role: requirement
  form: declaration
  topics:
    main_subject: CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Role := Requirement)/(.Header.Context.Form
      := Scope Unit Declaration)
  tier: 3
relations:
  is_replacement_for:
  - CA-R-3007
state:
  status: active
  version: 2
  updated_at: '2026-11-13T05:09:05.360312+00:00'
destination:
  file:
    name: CA-R-3075-CORE_META_MODEL-DECLARATION--declare-scope-unit-declaration-form.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
projection:
  source_carrier_path: ../../../.caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/CA-R-3075-CORE_META_MODEL-DECLARATION--declare-scope-unit-declaration-form.md
  source_atom_id: CA-R-3075
  source_atom_revision: 2
  source_sha256: 4a0ca350e71a8e3e925bb7892b51602d7fe52d7769f6a7abdc12fd05c247fded
  original_relations_sha256: dffc237e24daac59720a26ac5aa5371364f14e6328af89fc8d351b89bc328a59
---
## Summary

Declare Scope Unit Declaration Form

## Claim

### Prose Claim

Scope Unit Declaration is a Requirement Form. Its active Subject identifies one Scope Unit within the Project. Its Formal Claim states the unit’s stable ID, Name and ordering state. It states order.number when ordered. Label is optional. A non-Project Declaration states the unit’s direct Parent. The Project Declaration identifies the Project root and its unordered state.

### Formal Claim

```python
from caprmedio.formal_claims import declare_entity
from caprmedio.model import Requirement

class ScopeUnitDeclaration(Requirement):
    pass

declare_entity(
    entity_name="Scope Unit Declaration",
    entity_class=ScopeUnitDeclaration,
    qualification_property_path="Atom.Header.Context.Form",
    instance_relation_constraints={"HAS_ACTIVE_SUBJECT": {"target_entity_paths": ("Scope Unit",)}},
)
```
