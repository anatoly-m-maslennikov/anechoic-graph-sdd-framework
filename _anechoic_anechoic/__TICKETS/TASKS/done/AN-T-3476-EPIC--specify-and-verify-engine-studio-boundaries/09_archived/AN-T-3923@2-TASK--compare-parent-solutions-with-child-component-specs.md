---
atom_family: TKT
atom_id: AN-T-3923
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
relations:
  IS_REFERENCE:
  - AN-T-3489
  - AN-S-3368@6-draft
state:
  status: archived
  version: 2
  updated_at: '2026-11-25T13:23:25+00:00'
---
## Summary

Compare parent Solutions with child Component Specs

## Work

Use declared Component containment and pin the parent Solution and
the child's Manifest, Contract, and primary Solution. Match each
modeled delegation to the child operation. Check the interface and
inputs, the required guarantees, and the modeled outputs and effects.

Start with the Release dispatch to Local Release, Public Release,
and Runtime Images. Report each comparison with exact source links.

## Acceptance

Each checked delegation has separate verdicts against the child's
Manifest, Contract, and Solution. Show the differing fact for a
conflict. Leave missing or unsupported facts unresolved.

## Findings

C27's local, public, build-image, and run-image commands match the
first dispatch target and shared CLI entry point across the three
child Specs. Missing or ambiguous dispatch is unresolved. An explicit
wrong target is a conflict.

The inspected Solution pins include four additional child edges.
C43 → C45, C67 → C71, and C73 → C74 and C76 identify child effects.
Their shared call bindings remain unresolved. Arguments, results, and
guarantees beyond the Release CLI binding also remain open.
