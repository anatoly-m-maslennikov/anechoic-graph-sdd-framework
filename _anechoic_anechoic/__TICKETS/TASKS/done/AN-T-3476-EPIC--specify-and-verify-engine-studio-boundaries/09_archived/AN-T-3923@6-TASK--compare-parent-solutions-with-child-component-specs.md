---
atom_family: TKT
atom_id: AN-T-3923
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: archived
  version: 6
  updated_at: '2026-11-25T15:07:28+00:00'
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

C43 relies on C46 to display the result for a completed View Run.
The succeeded outcome requires the result display. The partial
outcome requires the result display and save error display. Both
outcomes match the C46 Draft Manifest, Contract, and Solution.
Removing the save error display conflicts with the partial case.

The browser receives the Project HTTP response through C21.
C45 remains the downstream owner of native query dispatch.

C73 requires a completed comparison of selected cases from C74
and identified file and Spec bindings from C76. Both report
effects match the respective child Manifest, Contract, and
Solution. The parent also requires separate coverage confirmation
from both children before reporting a complete analysis.

C67 requires accepted content paired with its generation ID
from C71. That outcome matches the C71 Draft Manifest, Contract,
and Solution. C71's SQL claim and artifact-read claim have
separate checks. A foreign instance or missing generation must
return no pair.

Structure representation, the read sequence, and exact content
and generation values remain open. Child coverage criteria and
call arguments remain open for the applicable delegations.
