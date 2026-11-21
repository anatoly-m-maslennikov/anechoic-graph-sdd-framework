---
atom_family: TKT
atom_id: AN-T-2957
structure:
  container:
    component: C14
  priority: 2
context:
  template: problem
state:
  status: active
  version: 1
  updated_at: '2026-11-21T16:25:45+00:00'
---
## Summary

Draft promotion scans and rebuilds the full Workbench index

## Claim

### Prose Claim

The Operator reports repeated Draft promotion waits of about two minutes.
The installed MCP checks the full Atom tree before writing, then scans it
again and replaces the Workbench projection before replying.

The production log recorded an 18-second projection rebuild. A separate
read-only probe in the production container took 75 seconds to capture
6,800 carriers and 19 ms to read one affected path.

## Current state

The checkout refreshes the recorded changed paths after a write. A regression
test verifies immediate visibility of the Current and Archived revisions
without a full projection. The installed runtime still uses the previous path.
The pre-write consistency check still reads the full tree.

## Resolution criteria

- Measure pre-write verification, publication, and Workbench refresh separately
  on a Project of comparable size.
- Keep ordinary promotion work proportional to the affected carriers. Preserve
  duplicate-revision checks, concurrent-edit checks, and immediate visibility.

## References

AN-T-2047, AN-T-2950.
