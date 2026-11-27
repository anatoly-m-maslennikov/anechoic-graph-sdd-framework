---
atom_family: TKT
atom_id: AN-T-3947
container:
  atom: AN-T-3476
priority: 2
context:
  template: task
  label: Task
state:
  status: "done"
  version: 1
  updated_at: "2026-11-27T02:07:27.735078+00:00"
---
## Summary

Review Component Specs against code and fix issues

## Work

Start after the preceding Epic tasks. Review each Component's
implementation against its pinned Manifest, Contract, and Solution.
Check boundaries, observable obligations, and the declared flow.
Fix confirmed issues in the owning Component.

## Acceptance

Record the reviewed source pins and evidence for each finding.
Verify the fixes with the relevant checks. Record any remaining
unverified obligations with their specific blockers.

## Findings

Reviewed 73 pinned Manifest, Contract, and Solution chains across the
Project. The inventory has 64 Components with Active Manifests and
nine Draft-only Components. The exact revision and hash ledger is
`an-t-3476-current-lean/all-73-final-pins.json` in the session evidence.

Fixed Workbench result binding, blocked lifecycle replies, Ticket
and metrics containment lookups, predecessor image admission, missing
metrics evidence, and formal-chain comparison errors. Focused tests
passed, including promotion through the real lifecycle socket.

Corrected Draft declarations for C19, C25, C27, C50, C56, C63, C73,
C74, and C81. The scope and evidence of each fix are recorded in
`an-t-3476-current-lean/an-t-3947-review.md` in the session evidence.

Left reserved and proposed call boundaries explicit. C67/C71 exact
locking and installed Structure reads, C74's alternate source-mode
CLI outcome, and C25 delivered placement remain unverified. The
review records the missing evidence or checker limit for each.
