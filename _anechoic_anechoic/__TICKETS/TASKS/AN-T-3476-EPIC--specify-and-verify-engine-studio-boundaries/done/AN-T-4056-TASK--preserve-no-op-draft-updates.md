---
atom_family: TKT
atom_id: AN-T-4056
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

Preserve no-op Draft updates

## Acceptance

Keep exact Draft bytes, Version and Updated At when the requested body
and authored Relations are unchanged. Return the existing artifact with
no modify receipt. Keep revalidation, refused writes and uncertain
publication. Correct the C16 CLI and effect scopes and check the
no-change case locally.

## Evidence

Exact Draft no-ops preserve Carrier bytes, Version, and Updated At.
The CLI returns the existing artifact with an empty effects list.
The C16 Drafts state the admitted families, governed effect, and
no-change outcome. Ten focused tests and the real CLI cases passed.
Lean matched 29 Action facts across five outcomes.
