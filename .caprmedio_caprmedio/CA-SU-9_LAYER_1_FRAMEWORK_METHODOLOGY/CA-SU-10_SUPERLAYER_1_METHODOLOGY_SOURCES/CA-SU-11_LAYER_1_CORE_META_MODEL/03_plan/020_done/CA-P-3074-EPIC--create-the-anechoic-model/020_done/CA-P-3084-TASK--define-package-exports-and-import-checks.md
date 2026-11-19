---
identity:
  atom_id: CA-P-3084
  ref_id: CA-P-3084
context:
  container:
    atom: CA-P-3074
  role: plan
  form: plan
  label: Task
  topics:
    main_subject: MODEL//CAPRMEDIO <+ Atom
  tier: 3
relations:
  IS_BLOCKED_BY:
  - CA-P-3083
state:
  status: done
  version: 1
  updated_at: '2026-11-18T21:56:49.875593+00:00'
destination:
  file:
    name: CA-P-3084-TASK--define-package-exports-and-import-checks.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/03_plan/020_done/CA-P-3074-EPIC--create-the-anechoic-model/020_done
---
## Summary

Define package exports and import checks

## Work

Test
   Internal defaults for all Package categories, Public and Internal
   allowlists, and caller rules inherited by nested ordinary Packages and
   child Components. Test `__<visibility>.<extension>` with normal Python
   imports. Check a behavior Contract with no export list and explicit
   nonempty and empty lists. Accept direct import of a named Unit and
   reject importing its whole Module when only the Unit is exported.

## References

CA-P-3074.
