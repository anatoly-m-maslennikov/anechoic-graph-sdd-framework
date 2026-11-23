---
atom_family: TKT
atom_id: AN-T-2083
container:
  atom: AN-T-2078
priority: 2
context:
  template: task
state:
  status: archived
  version: 2
  updated_at: 2026-11-11 00:15:31 +0400
---

## Summary

Verify shared Workbench View and transport behavior

## Objective

Exercise adopted View operations, result lifetime, schema naming, formatting, grid behavior and shared HTTP/MCP effects. Measure the Compact target. Keep real native Codex rendering and standalone-chat work deferred; do not count skipped cases as passes.

## Subtasks

- [ ] Confirm Current editor/display/transport acceptance and exclusive file ownership. (ETA: up to 15 min.)
- [ ] Verify one editor or View/Tab operation batch through the actual browser interface. Split before 20 min.
- [ ] Verify one theme, zoom or grid batch with the applicable Evaluations. Split before 20 min.
- [ ] Measure Compact at equivalent viewport/zoom against the recovered historical baseline; report a missing baseline explicitly. (ETA: up to 20 min.)
- [ ] Verify shared HTTP/MCP outcomes in a separate transport batch after Backend changes. Split before 20 min.
- [ ] Independently review/fix each result and record a small Work Report. (ETA: up to 15 min.)

## Definition of Done

The stated work has actual source/code/test evidence. Every unresolved or unrun case is explicit; no Task text replaces RMED.
