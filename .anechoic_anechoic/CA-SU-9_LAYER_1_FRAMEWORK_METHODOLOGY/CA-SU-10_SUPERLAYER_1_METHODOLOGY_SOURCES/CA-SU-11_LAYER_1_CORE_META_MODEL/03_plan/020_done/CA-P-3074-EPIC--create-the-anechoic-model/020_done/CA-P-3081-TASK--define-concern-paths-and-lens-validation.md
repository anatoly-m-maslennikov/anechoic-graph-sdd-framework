---
identity:
  atom_id: CA-P-3081
  ref_id: CA-P-3081
context:
  container:
    atom: CA-P-3074
  role: plan
  form: plan
  label: Task
  topics:
    main_subject: MODEL//ANECHOIC <+ Atom
  tier: 3
relations:
  IS_BLOCKED_BY:
  - CA-P-3080
state:
  status: done
  version: 1
  updated_at: '2026-11-18T21:56:29.201112+00:00'
destination:
  file:
    name: CA-P-3081-TASK--define-concern-paths-and-lens-validation.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/03_plan/020_done/CA-P-3074-EPIC--create-the-anechoic-model/020_done
---
## Summary

Define Concern paths and lens validation

## Work

Verify
   the three Concern fields, full paths, and both hops in
   `Model/Graph/Node//Artifact`. Cover absent, inherited, and explicit
   empty lens whitelists. Accept SPEC with DES and SWE. Accept SWE with
   SWD and QA when DevOps is omitted. Reject sibling DES and SYS because
   both cover DOM.

## References

CA-P-3074.
