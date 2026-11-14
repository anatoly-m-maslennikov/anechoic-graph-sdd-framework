---
identity:
  atom_id: CA-C-740
  ref_id: CA-C-740
context:
  role: concern
  form: Problem
  container:
    scope_unit: CA-SU-45
  concern:
    priority: Medium
  tier: 3
  topics:
    main_subject: CAPRMEDIO_MODEL <+ Atom
relations:
  CONCERN_ABOUT:
  - CA-R-3067
  - CA-R-924
  - CA-P-2738
  - CA-P-3022
state:
  version: 1
  status: active
  updated_at: '2026-11-13T18:37:53.961055+00:00'
destination:
  file:
    name: CA-C-740-WORKBENCH_BACKEND-PROBLEM--workbench-audits-flag-valid-plan-forms-and-placements.md
    path: .caprmedio_caprmedio/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-20_FEATURE_APPS/CA-SU-43_APP_WORKBENCH/CA-SU-45_FEATURE_WORKBENCH_BACKEND/01_concern
---
## Summary

Workbench audits flag valid Plan forms and placements

## Concern

Workbench reports two false positives for valid Plan Atoms. This makes genuine carrier and schema problems harder to distinguish during in-place cleanup.

## Details

- **Placement.** `atom_declared_carrier_issues` reports that CA-P-2738 should be under the Project root's `03_plan/020_done`. Its declared path and physical carrier correctly sit under the CA-P-2715 Epic. The audit builds a Scope Unit lookup containing a `None` key for the Project root. When the child declares `container.atom` and has no `scope_unit`, the placement check takes that root entry and skips the declared Atom parent.
- **Schema.** `atom_schema_issues` reports `Form is not declared: Plan` for CA-P-3022, whose Role and Form are Plan/Plan. CA-R-924 explicitly admits that pair. The schema audit checks a global list of compiled literal Forms that omits Plan, so the resulting diagnosis conflicts with the applicable Role/Form admission.

## Acceptance

- A correctly nested Plan produces no declared path issue, even when the Project root has no Scope Unit ID. A misplaced child still reports its expected path under the declared Atom parent.
- An admitted Plan/Plan carrier produces no unknown-Form issue. An actually unsupported Form or disallowed Role/Form pair still produces a schema diagnostic.
- Verify both through the Workbench audit tables with representative valid and invalid carriers.