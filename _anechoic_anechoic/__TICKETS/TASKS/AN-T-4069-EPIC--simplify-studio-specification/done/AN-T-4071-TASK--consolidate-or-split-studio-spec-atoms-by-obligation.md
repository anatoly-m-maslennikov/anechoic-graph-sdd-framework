---
atom_family: TKT
atom_id: AN-T-4071
container:
  atom: AN-T-4069
priority: 2
context:
  template: task
  label: Task
state:
  status: done
  version: 1
  updated_at: "2026-11-27T14:51:20+00:00"
---

## Summary

Consolidate or split Studio Spec Atoms by obligation

## Acceptance

Review Studio architecture and QA Atoms for overlapping or
mixed responsibilities. Merge or retire only when an Active
authority preserves the obligation and references. Split a
mixed Atom where distinct owners or guarantees warrant it.

## Evidence

AN-S-3389 delegates repeated startup and Builder rules to
AN-S-3337 and AN-S-3334. AN-S-3290 now owns the Local Release
gate sequence, and AN-S-4734 is Archived. AN-S-4738 owns
Fast Local Release timing. C19 documents legacy test discovery
and uses the current Manifest binding AN-S-3055@29.
