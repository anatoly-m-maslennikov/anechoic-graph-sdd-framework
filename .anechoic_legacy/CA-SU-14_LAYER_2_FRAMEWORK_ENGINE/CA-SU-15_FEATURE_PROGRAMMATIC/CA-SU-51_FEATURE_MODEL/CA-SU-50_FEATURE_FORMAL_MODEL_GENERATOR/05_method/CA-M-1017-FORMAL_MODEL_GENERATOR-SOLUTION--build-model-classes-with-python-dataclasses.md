---
identity:
  atom_id: CA-M-1017
  ref_id: CA-M-1017
context:
  role: method
  form: solution
  tier: 3
  container:
    scope_unit: CA-SU-50
  topics:
    main_subject: ANECHOIC_STRUCTURE <+ Scope Unit//FORMAL_MODEL_GENERATOR
state:
  version: 1
  status: active
  updated_at: '2026-11-13T16:16:47.381063+00:00'
destination:
  file:
    name: CA-M-1017-FORMAL_MODEL_GENERATOR-SOLUTION--build-model-classes-with-python-dataclasses.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-51_FEATURE_MODEL/CA-SU-50_FEATURE_FORMAL_MODEL_GENERATOR/05_method
relations:
  CONTRIBUTES_TO:
  - CA-R-3137
---
## Summary

Build Model classes with Python dataclasses

## Claim

### Prose Claim

- Read Nodes and Properties from `declare_entity` and Relations from `declare_relation` in Python Formal Claims.
- Generate Model classes with the standard Python `@dataclass` decorator. Use class inheritance for narrower kinds.
- Keep named instance checks in their Declaring Claims and supply them to MODEL_VALIDATION through its separate checks module.
- MODEL_VALIDATION checks the complete proposed instance at the write boundary. It uses the declared types, allowed values, cardinalities, Relation contracts, and applicable named checks.
