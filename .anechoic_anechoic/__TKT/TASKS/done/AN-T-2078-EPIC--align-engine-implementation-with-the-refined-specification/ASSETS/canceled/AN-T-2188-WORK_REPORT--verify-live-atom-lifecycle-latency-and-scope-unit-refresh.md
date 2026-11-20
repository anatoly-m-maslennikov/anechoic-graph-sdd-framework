---
atom_family: TKT
atom_id: AN-T-2188
structure:
  container:
    atom: AN-T-2078
  priority: 2
context:
  template: work_report
state:
  status: canceled
  version: 1
  updated_at: '2026-11-12T00:01:59.664109+04:00'
---

## Summary

Verify live Atom lifecycle latency and Scope Unit refresh

## Details

CA-P-3006. Local image `sha256:a72ddb581001e00ab529871736cc7ce399950e0baa82fbd89f8a36ccf08d0932`.

- Lifecycle used a Scope Unit created after MCP startup. Both seeded cases passed all six operations, form cancellation, stale-Version rejection, and cleanup in the same container.
- The replacement Update took 109.7 seconds. The same-ID Update took 78.2 seconds. Both returned within the original 180-second limit.
- The focused lifecycle tests and both Workbench Docker guards passed. Health, Workbench frontend and query, and MCP discovery passed on the activated image.
