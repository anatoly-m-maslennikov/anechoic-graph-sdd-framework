---
atom_family: SPEC
atom_id: AN-S-1968
container:
  component: C21
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 3
  updated_at: '2026-11-12T12:38:36.006807+00:00'
---
## Summary

Measure live Atom Lifecycle Tools

## Claim

### Prose Claim

Measure each of the six live MCP Atom Lifecycle Tools from request to response on twenty randomized Atoms in one temporary Scope Unit. Verify the effects through Workbench. Record the running image, individual durations, median, maximum, and cleanup.

## Details

Include same-ID and replacement Update. Check that Create Draft without a source Version copies Current and an explicit Version copies exactly that revision. Check that fields absent from the request are preserved. Include distinct padded and unpadded decimal Atom IDs and verify selection preserves the exact spelling. Check independent Archive and Promote Draft batches for result order, stopping on the first failure, and accurate completed and remaining targets. Confirm grouped publication with no missing changed rows.

Check that a Current Epic can change from Backlog to Active with a Draft child. Verify that direct and nested Current Tasks become Active and the Draft child stays a Draft. Run a content-only Update of an Epic with children and verify that the children’s content and Status are unchanged.

Check independent copying separately. Copy a Current Atom and a Draft through Create Draft. Verify that each copy starts at Version 1 with a new ID, preserves all fields not supplied in the request and leaves the source unchanged. Promoting the copy must leave the source in place.
