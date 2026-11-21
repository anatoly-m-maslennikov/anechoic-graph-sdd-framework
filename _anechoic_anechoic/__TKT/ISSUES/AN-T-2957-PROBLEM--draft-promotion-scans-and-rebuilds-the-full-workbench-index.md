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
  version: 2
  updated_at: '2026-11-21T17:50:46.330939+00:00'
---
## Summary

Draft promotion scans and rebuilds the full Workbench index

## Claim

### Prose Claim

The Operator reports repeated Draft promotion waits of about two minutes.
Before the first fix, MCP checked the full Atom tree before writing, then
scanned it again and replaced the Workbench projection before replying.

The production log recorded an 18-second projection rebuild. A separate
read-only probe in the production container took 75 seconds to capture
6,800 carriers and 19 ms to read one affected path.

## Current state

The installed runtime refreshes the recorded changed paths after each write.
The checkout verifies the indexed population with file metadata. It reads
changed or new carriers and retains duplicate and concurrent-edit checks.
Local Release is pending for the pre-write fix.

## Verification

A Docker rehearsal on 6,816 carriers measured 1.79 s for pre-write
verification, 5 ms for publication, and 171 ms for Workbench refresh.
Promotion returned in 1.99 s with the Current and Archived revisions
immediately queryable. 104 focused tests passed.

## Resolution criteria

- Measure pre-write verification, publication, and Workbench refresh separately
  on a Project of comparable size.
- Keep ordinary promotion work proportional to the affected carriers. Preserve
  duplicate-revision checks, concurrent-edit checks, and immediate visibility.

## References

AN-T-2047, AN-T-2950.
