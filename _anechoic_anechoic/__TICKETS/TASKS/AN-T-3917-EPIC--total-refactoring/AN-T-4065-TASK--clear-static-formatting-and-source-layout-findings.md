---
atom_family: TKT
atom_id: AN-T-4065
container:
  atom: AN-T-3917
priority: 2
context:
  template: task
  label: Task
state:
  status: in_queue
  version: 1
  updated_at: '2026-11-27T12:46:01+00:00'
---

## Summary

Clear Static formatting and source layout findings

## Acceptance

Use the committed formatter and the full-checkout line and source
size checks. Resolve each finding without changing supported
behavior. Preserve exact fixtures and generated artifact checks.
Retain every selected test and its normal discovery path. Verify
the 79-character, 45-line and 300-line limits where they apply.

## Progress

The checked formatting pass preserved Python syntax trees and avoided
new 45/300 violations. It kept the imported Markdown fixtures and the
hash-bound generated Scope predicate intact. Narrow formatter directives
retain required wraps for long imports.

The 2026-11-27 Static run reports 839 files that need formatting,
24,642 overlength lines, and eight size findings. The previous run
reported 869 files, 34,692 lines, and 11 size findings. All remaining
size findings are in Model Generator.
