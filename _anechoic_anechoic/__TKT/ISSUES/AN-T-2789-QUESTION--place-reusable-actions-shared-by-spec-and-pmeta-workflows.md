---
atom_family: TKT
atom_id: AN-T-2789
structure:
  container:
    component: C00
  priority: 2
context:
  template: question
state:
  status: active
  version: 1
  updated_at: '2026-11-19T09:08:06.137665+00:00'
---
## Summary

Place reusable Actions shared by SPEC and PMETA Workflows

## Concern

Should the migration keep one SPEC history for each reusable Action that both SPEC and PMETA Workflows invoke?

## Details

The reusable Source Reconciliation and Applicable Methodology Workflows CA-O-010 and CA-O-011 invoke CA-O-004 through CA-O-008. The PMETA Release Readiness Workflow CA-O-025 also invokes all five. Together these Actions have 109 held revisions.

Proposed disposition. Keep one SPEC history per reusable Action. Preserve verified calls from both Workflow families and place each owned Step with its Workflow. Keep each unresolved exact revision binding in the migration receipt.

## References

CA-P-3075, CA-O-010, CA-O-011, CA-O-025.
