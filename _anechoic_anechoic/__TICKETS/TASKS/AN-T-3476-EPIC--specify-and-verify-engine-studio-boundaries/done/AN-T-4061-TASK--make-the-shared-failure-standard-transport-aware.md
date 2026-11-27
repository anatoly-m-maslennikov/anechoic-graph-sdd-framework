---
atom_family: TKT
atom_id: AN-T-4061
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: '2026-11-27T11:26:53+00:00'
---

## Summary

Make the shared failure Standard transport aware

## Acceptance

Refine existing Programmatic Standards to prescribe shared typed
failure handling by default. Preserve the operation result, cause
and diagnostics. Use each transport's declared result and exit
semantics, including valid denial envelopes. Keep local transitions
and effects in each Solution.

## Evidence

AN-S-5072@2-draft prescribes shared operation failure handling by
default and delegates response or exit status semantics to the
Component Contract. Lean checked response failure at exit zero,
missing failure response, nonzero-exit contracts and background
diagnostics. AN-T-4063 owns default applicability resolution and
the public SourceError preservation check.
