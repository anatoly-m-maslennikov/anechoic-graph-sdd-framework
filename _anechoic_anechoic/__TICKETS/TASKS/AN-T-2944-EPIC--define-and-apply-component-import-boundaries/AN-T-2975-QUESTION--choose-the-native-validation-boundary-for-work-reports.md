---
atom_family: TKT
atom_id: AN-T-2975
container:
  atom: AN-T-2944
priority: 2
context:
  template: question
state:
  status: "in_queue"
  version: 2
  updated_at: "2026-11-22T04:00:15.620612+00:00"
---
## Summary

Choose the native validation boundary for Work Reports

## Situation

AN-S-2598@4 requires exactly one IS_WORK_REPORT_FOR target of Plan Form.
AN-S-2752@36 also requires the Work Report to copy the Task Summary and
Container. The legacy candidate compiler binds the target constraint
against Model classes.

Native placement tests cover the Work Report destination. The inspected
native write paths supply no matching target validation evidence.
Workbench schema compilation does not establish enforcement of authored
Content constraints during native writes.

An isolated Project fixture exercised the native lifecycle dispatcher.
It accepted a work_report with the default Project container and only
a Summary. The saved carrier had neither a Task Relation nor Details.

## Decision needed

Identify the native write interface that admits Work Reports and applies
their Relation and Content rules. If the native representation changed,
identify the Current Spec that defines its replacement.

## Acceptance

Exercise the actual native entry point. Accept a Work Report with one
admitted Task target. Refuse missing, multiple, and wrong-Form targets.
Verify the authored Content constraints at the same boundary before
retiring the corresponding legacy compiler path.

## References

AN-T-2944, AN-T-2751, AN-S-2598@4, and AN-S-2752@36.
