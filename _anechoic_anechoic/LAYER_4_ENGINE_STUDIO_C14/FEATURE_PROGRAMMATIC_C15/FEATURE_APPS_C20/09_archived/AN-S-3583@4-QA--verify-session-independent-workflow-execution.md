---
atom_family: SPEC
atom_id: AN-S-3583
container:
  component: C20
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 4
  updated_at: 2026-10-23 03:14:50 +0400
---
## Summary

Verify session-independent Workflow execution

# Summary

Verify session-independent Workflow execution

## Scope

WORKFLOW_ORCHESTRATOR's initial local execution capability.

## Claim

the Evaluation **must** verify independent execution through mock Agent end-to-end cases **and** the real DBOS queue.

## Details

- queue a Run from a short-lived client, disconnect it, start a separate worker **and** verify recorded gather/check/fix results.
- verify clean checks, admitted fixes, blocked reports, Agent failure, timeout, duplicate requests **and** mismatched identities.
- verify worker restart acknowledges a previously applied after hash rather than repeating the edit.
- verify no recheck phase is introduced **and** initial findings remain **in** the saved report.
- distinguish mock execution from a live Codex model Run; mock passes prove integration boundaries, **not** semantic review quality.
