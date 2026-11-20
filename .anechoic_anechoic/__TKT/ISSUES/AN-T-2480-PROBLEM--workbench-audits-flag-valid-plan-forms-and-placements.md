---
atom_family: TKT
atom_id: AN-T-2480
structure:
  container:
    component: C45
  priority: 2
context:
  template: problem
state:
  status: active
  version: 1
  updated_at: '2026-11-13T18:37:53.961055+00:00'
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