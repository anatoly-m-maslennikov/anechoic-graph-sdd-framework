---
identity:
  atom_id: AN-T-2377
context:
  container:
    component: C00
  template: problem
state:
  status: resolved
  version: 2
  updated_at: 2026-10-23 03:14:50 +0400
---
# Summary

Separate committed state recovery from concurrent edits

## Concern

The initial recovered-state Journal preparation for commit4c16aee45 stopped before appending because P1376 had already changed in the working tree. Its correct byte-equality guard prevented falsely claiming that the later working state belonged to that commit.

## Evidences

Root reopened the exact eleven saved Carrier states from that actual commit, excluding concurrent edits, and sealed eleven recovered-state Events. Actual append receipts matched prediction; reopened NDJSON matched all eleven validated Events. The record concerns those committed historical states, not current working bytes or save-Tool completion. The failed attempt appended nothing.

## Blast radius

Only this committed-state Journal recovery. Concurrent review work was preserved. Later changed Carrier states require their own truthful save disposition; no review, source or runtime gate is waived.
