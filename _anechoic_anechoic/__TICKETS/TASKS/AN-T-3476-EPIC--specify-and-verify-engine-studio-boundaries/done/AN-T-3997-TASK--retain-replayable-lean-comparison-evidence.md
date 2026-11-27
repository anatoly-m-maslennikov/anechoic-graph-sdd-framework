---
atom_family: TKT
atom_id: AN-T-3997
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: "done"
  version: 1
  updated_at: "2026-11-27T03:14:08.236500+00:00"
---
## Summary

Retain replayable Lean comparison evidence

## Acceptance

Save the independently generated Lean from the authored Specs and the
implementation. Keep the exact Lean comparison program, source digests,
and coverage by Action and outcome. Distinguish a translation match from
a code match.

Replay a matching chain and a conflicting chain. Report unsupported
implementation evidence as unresolved. Clear a stale passing receipt
when a new run fails.

Verify that translation validation finishes before comparison and that
Lean and Mermaid use the same validated Solution. Keep ordering
requirements where a later operation depends on the earlier result.
