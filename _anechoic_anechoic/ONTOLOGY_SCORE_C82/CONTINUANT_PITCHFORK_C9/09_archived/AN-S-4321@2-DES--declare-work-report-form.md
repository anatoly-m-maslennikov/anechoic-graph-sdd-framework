---
atom_family: SPEC
atom_id: AN-S-4321
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 2
  updated_at: 2026-11-08 19:06:46 +0400
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
Atom/(.Header.Form := Work Report);

Atom/(.Header.Form := Work Report).Content.Details:: {::1};

Atom/(.Header.Form := Work Report).Content.Details.*[]{::0};

Atom/(.Header.Form := Work Report).Content.Summary ;> Atom/(.Header.Form := Work Report).Content.Details;

# instances
$report[<Atom>, (.Header.Form = Work Report)];

$report.Header.Role == Plan;

$report {::1}((IS_WORK_REPORT_FOR)) $task[<Atom>, (.Header.Role = Plan) AND (.Header.Form = Plan)];

$report.Header.ID != $task.Header.ID;

$report.Content.Summary == $task.Content.Summary;

$report.Header.Container == $task.Header.Container
```

## Semantics

A Work Report is the evolving record of a Task’s execution.
