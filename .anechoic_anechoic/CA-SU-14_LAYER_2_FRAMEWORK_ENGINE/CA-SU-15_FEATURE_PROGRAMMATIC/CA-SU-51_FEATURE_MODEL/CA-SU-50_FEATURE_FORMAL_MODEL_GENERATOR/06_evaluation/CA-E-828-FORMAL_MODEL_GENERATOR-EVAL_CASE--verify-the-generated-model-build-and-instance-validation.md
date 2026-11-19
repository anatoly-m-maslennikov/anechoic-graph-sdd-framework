---
identity:
  atom_id: CA-E-828
  ref_id: CA-E-828
context:
  role: evaluation
  form: Eval Case
  tier: 3
  container:
    scope_unit: CA-SU-50
  topics:
    main_subject: ANECHOIC_STRUCTURE <+ Scope Unit//FORMAL_MODEL_GENERATOR
state:
  version: 1
  status: active
  updated_at: '2026-11-13T17:18:13.986621+00:00'
destination:
  file:
    name: CA-E-828-FORMAL_MODEL_GENERATOR-EVAL_CASE--verify-the-generated-model-build-and-instance-validation.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-51_FEATURE_MODEL/CA-SU-50_FEATURE_FORMAL_MODEL_GENERATOR/06_evaluation
---
## Summary

Verify the generated Model build and instance validation

## Claim

### Prose Claim

1. Build the selected ANECHOIC Model. Import the generated package and verify that a narrower class inherits its declared base. Verify that package contents follow CA-R-3136.
2. Build with a missing parent, an inheritance cycle, an unresolved Relation endpoint, and an invalid Python Claim. Each case reports an error to stderr and stops the build.
3. At the instance write boundary, accept a valid proposed instance. Reject an undeclared Property, incorrect value type, inadmissible value, and a cardinality or Relation violation before writing.
4. Submit a batch with a valid target followed by an invalid target and another valid target. Verify the first write remains applied, the error is reported to stderr, and processing stops at the invalid target.
