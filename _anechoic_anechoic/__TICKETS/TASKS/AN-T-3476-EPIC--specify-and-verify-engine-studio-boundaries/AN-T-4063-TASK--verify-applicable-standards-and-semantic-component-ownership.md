---
atom_family: TKT
atom_id: AN-T-4063
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 2
  updated_at: '2026-11-27T12:13:22.499691+00:00'
---

## Summary

Verify applicable Standards and semantic Component ownership

## Acceptance

AN 1 owns this task. Resolve one default Standard to an exact pin
and check its use through C95 SourceError and C94 incomplete results.
Check source and field preservation with a negative control. Add a
semantic owner and provider check and reject swapped scheduler roles.
Preserve explicit child roles and empty entry points.

## Handoff

Queued to AN 1 with the source review, exact Lean evidence, and
negative controls.
AN-S-5072@2-draft is the revised shared failure Standard.

## Verification

Checked the nominated AN-S-5072@2-draft pin and its C15 default scope
through the Active C75, C94, and C95 Manifest ownership chain. A real
C95 SourceError and the C94 incomplete response retain the same
source, field, role, and message. Lean rejects missing diagnostics
and missing response failure.

The C32 check independently pins the C41 and C42 provider Manifests.
Lean rejects swapping their roles in both C32 declarations. The check
preserves explicit child roles and empty entry points.

The Standard remains a Draft. Runtime-wide default selection and
installed behavior require separate evidence.
