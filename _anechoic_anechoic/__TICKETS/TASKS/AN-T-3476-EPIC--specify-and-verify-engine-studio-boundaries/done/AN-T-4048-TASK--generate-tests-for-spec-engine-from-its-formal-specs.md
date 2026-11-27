---
atom_family: TKT
atom_id: AN-T-4048
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
relations:
  IS_BLOCKED_BY:
  - AN-T-4047
state:
  status: "done"
  version: 1
  updated_at: "2026-11-27T02:09:26.005933+00:00"
---
## Summary

Generate tests for Spec Engine from its formal Specs

## Acceptance

Use the existing generator with the pinned Manifests, embedded Contracts,
and Solutions of Spec Engine and its in-scope children. Generate cases
when the formal declarations determine the inputs and expected outcomes.
Keep C50 Formal Model Generator and its Seeds outside this Task.

Run generated cases through the owning Component's normal entry point
in the Functional suite. Cover success and declared error outcomes.
Record the source pins, generated cases, results, and obligations that
need hand-authored tests.

## Evidence

The Functional suite now runs a Spec Engine self-verification case using
the exact C94 Manifest and Solution. The case generator selects a required
effect from the formal comparison and changes its outcome in a snapshot.
Lean finds the conflict. The same suite checks nominal verification and
explicit errors for stale or malformed source inputs.

The workflow mutation uses the pinned Specs as fixtures. C92 continues to
generate bounded byte-framing cases for framing declarations.

The C94 suite passed four checks. It derives a required-effect mutation
for each terminal outcome, including the incomplete diagnostic. The
inventory review found no literal framing inputs in the 16 Spec Engine
pairs. C51 has no executable entry point. The other runtime Actions need
hand-authored input fixtures. C93's symbolic bindings need event values
before Lean can prove or refute the bound effects.
