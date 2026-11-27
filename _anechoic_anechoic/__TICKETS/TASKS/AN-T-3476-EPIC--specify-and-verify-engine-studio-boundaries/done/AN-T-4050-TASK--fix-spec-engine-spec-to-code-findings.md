---
atom_family: TKT
atom_id: AN-T-4050
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
relations:
  IS_BLOCKED_BY:
  - AN-T-4049
state:
  status: "done"
  version: 1
  updated_at: "2026-11-27T02:23:47.276105+00:00"
---
## Summary

Fix Spec Engine Spec-to-code findings

## Acceptance

Fix each confirmed finding at its owning Spec or Component. Preserve
the accepted Contract when correcting implementation behavior. Keep C50
Formal Model Generator and its Seeds outside the edit scope.

Rerun the relevant comparisons and Functional tests, including generated
cases. Record the disposition and verification evidence for each finding.

## Evidence

The fixes preserve diagnostic source pins, reject malformed snapshot
Headers with structured errors, validate the offline Project Manifest
against the supplied Model, and compare legacy Manifest pins as source
pins. Lean checks reject null or blank identities and empty witness sets.

Focused Functional regressions, Code Access checks for the generated test,
and scoped Ruff checks passed. Session evidence includes
`spec-engine-final-functional.xml` and `spec-engine-typed-identities.xml`.

The repeat-review fixes cover Structure classifiers and Tier 1
checkpoints, explicit sibling entry and HTTP routes, and direct
mixed-profile selection. The disposable restart and 46 focused verifier
checks passed. Separate reports record the remaining symbolic witness
limits and the unchanged historical static findings.
