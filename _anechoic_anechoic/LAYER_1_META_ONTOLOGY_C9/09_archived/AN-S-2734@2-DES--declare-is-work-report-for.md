---
atom_family: SPEC
atom_id: AN-S-2734
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

Declare IS_WORK_REPORT_FOR

## Claim

### Prose Claim

The Host is a Plan / Work Report. The Target is the reported work Plan with Form Plan.

### Formal Claim

```CFEL
# model
Relation//IS_WORK_REPORT_FOR ((HAS_CLASSIFICATION)) Derivation == Direct;

# instances
$report[<Atom>, (.Header.Context.Role = Plan) AND (.Header.Context.Form = Work Report)] ((IS_WORK_REPORT_FOR)) $task[<Atom>, (.Header.Context.Role = Plan) AND (.Header.Context.Form = Plan)]
```

## Semantics

IS_WORK_REPORT_FOR relates a Work Report to its Task.
