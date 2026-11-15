---
identity:
  id: CA-R-3053
  ref_id: CA-R-3053
context:
  container:
    scope_unit: CA-SU-11
  role: Requirement
  form: Declaration
  topics:
    main_subject: CAPRMEDIO_MODEL <+ Atom/(.Header.Context.Form := Work Report)
  tier: 3
state:
  status: active
  version: 4
  updated_at: '2026-11-13T22:57:24.985880+00:00'
destination:
  file:
    name: CA-R-3053-CORE_META_MODEL-DECLARATION--declare-work-report-form.md
    path: .caprmedio_caprmedio/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement
---

## Summary

Declare Work Report Form

## Claim

### Prose Claim

A Work Report records the execution of one Plan with Form Plan in a separate Atom. This is the reported Task. It has its own ID and the same Summary and Container as that Task. IS_WORK_REPORT_FOR identifies the Task by its base Atom ID.

Details records:

- actual changes;
- checks performed;
- results;
- remaining gaps.

The report is updated throughout execution. Its Status describes the reporting work: Active while maintained, Done when the final known changes, checks, results and remaining gaps are recorded, or Canceled when reporting is abandoned. Completed reporting includes explicit remaining gaps. The Task retains its own Status.

### Formal Claim

```python
from caprmedio.formal_claims import declare_entity
from caprmedio.model import Plan

class WorkReport(Plan):
    pass

declare_entity(
    entity_name='Work Report', entity_class=WorkReport,
    qualification_property_path='Atom.Header.Context.Form',
    form_roles=('Plan',),
    instance_relation_constraints={
        'IS_WORK_REPORT_FOR': {
            'target_entity_paths': ('Atom/(.Header.Context.Role:=Plan)/(.Header.Context.Form:=Plan)',),
            'targets_per_source': 1,
        },
    },
    form_content={'required_value': 'Details', 'no_children': 'Details', 'after': 'Summary'},
)
```

## Semantics

A Work Report is the evolving record of a Task’s execution.
