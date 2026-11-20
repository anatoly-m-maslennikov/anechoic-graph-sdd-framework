---
identity:
  atom_id: AN-T-2187
context:
  container:
    atom: AN-T-2078
  tier: 4
  template: task
state:
  status: canceled
  version: 1
  updated_at: '2026-11-11T23:40:04.931365+04:00'
---

## Summary

Fix live Atom lifecycle latency and Scope Unit refresh

## Objective

- Make lifecycle writes accept new Scope Units without an MCP restart.
- Remove redundant filesystem work that caused the live Update call to exceed 180 seconds.
- Rerun the seeded live lifecycle checks and record MCP response times, Workbench visibility, and fixture cleanup.
