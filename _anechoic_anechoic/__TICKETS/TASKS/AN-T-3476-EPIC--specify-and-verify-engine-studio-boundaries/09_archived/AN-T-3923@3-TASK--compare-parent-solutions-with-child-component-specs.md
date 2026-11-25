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
  - AN-S-4801@2-draft
  - AN-S-3060@9-draft
  - AN-S-3306@3-draft
  - AN-S-3372@3-draft
state:
  status: archived
  version: 3
  updated_at: '2026-11-25T13:54:14+00:00'
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

C43 relies on C46 to show the View Run result. Lean matches the
`workbench_frontend_run_view` success effect against C46's Draft
Manifest, Contract, and Solution. Removing or bypassing the
display effect conflicts with that requirement.

The browser receives the Project HTTP response through C21.
C45 remains the downstream owner of native query dispatch.

C67 → C71 and C73 → C74 and C76 identify child effects with
open call bindings. Arguments and exact returned values remain
open for the checked delegations.
