---
atom_family: SPEC
atom_id: AN-S-2598
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 3
  updated_at: 2026-11-11 14:06:22 +0400
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

```CFEL
# model
Atom.Header.Context.Form :: Work Report;

Atom/(.Header.Context.Role in (Plan))/(.Header.Context.Form in (Work Report)).Content.Details:: {::1};

Atom/(.Header.Context.Role in (Plan))/(.Header.Context.Form in (Work Report)).Content.Details.*[]{::0};

Atom/(.Header.Context.Role in (Plan))/(.Header.Context.Form in (Work Report)).Content.Summary ;> Atom/(.Header.Context.Role in (Plan))/(.Header.Context.Form in (Work Report)).Content.Details;

# instances
FOR EACH $report[<Atom>, (.Header.Context.Form = Work Report)]:
(
    $report.Header.Context.Role == Plan;

    $report {::1}((IS_WORK_REPORT_FOR)) $task[<Atom>, (.Header.Context.Role = Plan) AND (.Header.Context.Form = Plan)];

    $report.Header.Identity.ID != $task.Header.Identity.ID;

    $report.Content.Summary == $task.Content.Summary;

    $report.Header.Context.Container == $task.Header.Context.Container
)
```

## Semantics

A Work Report is the evolving record of a Task’s execution.
