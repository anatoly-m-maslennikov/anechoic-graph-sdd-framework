---
identity:
  atom_id: AN-S-1256
context:
  container:
    component: C15
  tier: 3
  lens: SWD
state:
  status: draft
  version: 14
  updated_at: '2026-11-14T08:28:20.314145+00:00'
---
## Summary

Bound resource use to the workload

## Claim

### Prose Claim

For new or changed PROGRAMMATIC implementation, account for input size and resource growth.
Use bounded or incremental processing, controlled concurrency and suitable budgets to prevent uncontrolled growth and resource exhaustion, including out-of-memory failures.

## Details

- Scope includes Tools, Apps, MCP adapters and tests.
- Use streaming, batching, bounded buffers or bounded work admission where they meet declared behavior.
- Budget aggregate concurrent work, memory, queues, workers, subprocesses, and retained state.
- Put concrete limits in configuration and implementation. Evaluation owns resource-behavior verification and acceptance.
- This Method sets no product, concurrency count or universal threshold.
