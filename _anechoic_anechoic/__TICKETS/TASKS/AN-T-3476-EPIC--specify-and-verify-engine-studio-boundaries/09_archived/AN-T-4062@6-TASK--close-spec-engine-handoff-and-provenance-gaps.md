---
atom_family: TKT
atom_id: AN-T-4062
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: archived
  version: 6
  updated_at: "2026-11-27T20:39:38.396618+00:00"
---

## Summary

Close Spec Engine handoff and provenance gaps

## Acceptance

AN 1 owns this task. Cover C50 Purpose and the C75/C50/C53/C93
same-Model handoff including fallback. Bind C94 stage evidence and
C75 compile_workflow to the same Model. Specify C95/C83 exact source
identity and C90 verdict aggregation. Verify the pinned Specs, Lean
and focused behavior.

## Handoff

Queued to AN 1 with the source review, exact Lean evidence, and
negative controls.

## Verification

Published versioned Manifest and Solution changes for C75, C50,
C53, C93, C94, C95, C83, and C90. Lean accepted all twelve selected
Action translations. Their static value-binding checks still have
unresolved obligations.

The staged native checks passed for compiled, reused, and fallback
Models. C53 opened the Model that C93 used. The staged descriptor
digest agreed with the returned value. C75 sent the same normalized
workflow Model to the renderer and the caller.

C94 now rejects changed Model, source, Action, diagram, and framing
results. C95 and C83 preserve the exact selected source pins. The
public C90 proof checks verdict precedence on every modeled list of
strings and rejects its precedence mutation.

Focused Functional checks passed. 
The isolated Local Release passed host preflight on port 57153.
The static gate then found 560 Ruff lint errors in unchanged
baseline files. It also reported formatting, Source Language,
import ownership, and State findings. The image build did not
start. The Task remains In Queue pending a passing Local Release.

## Current revision check

C93 and C75 pin AN-S-5018@8. C50 Manifest AN-S-3065@40 also pins that
version. It and Solution AN-S-5015@3 use C53.admitted_model. Lean
matches the C53 provider Contract for the reuse, compile, and fallback
handoffs. The generated C50 CLI test passed.

Concrete Lean checks matched the selected Model and descriptor through
C53 opening, C93 compilation, and return for all three branches. The
static verifier still leaves bound value obligations unresolved.

The current Static gate failed. Ruff lint passed, and format reported
434 files. Source size reported 48 findings and Source Language reported
three. No candidate image was built in this check. Local Release remains
open.

## Current handoff verification

All eleven selected parent-to-child calls match in Lean at their
current source pins, including C75 to C93 and C94 framing validation.

The C93 compiler split passed Ruff, the 45/300 limits, both import
checks, and all 21 C93 tests. Lean matched observed staged and offline
results. Wrong Manifest pins, changed carrier digests and changed
Purpose values were rejected. C95 confirmed the current pins in both
source modes and refused stale revisions.

Full Static still blocks Local Release outside the C93 checks.

## C50 handoff test discovery

The existing case now loads in the Project test runner and under
pytest. The runner passed all four generated C50 outcomes. The test
uses the same current Manifest and Solution pins. Local Release still
requires a passing Static gate.
