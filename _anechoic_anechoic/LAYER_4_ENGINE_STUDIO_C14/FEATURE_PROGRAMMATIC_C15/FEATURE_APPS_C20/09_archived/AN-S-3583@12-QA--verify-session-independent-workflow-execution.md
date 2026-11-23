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
  version: 12
  updated_at: 2026-11-09 07:45:14 +0400
---

## Summary

Verify session-independent Workflow execution

## Claim

### Prose Claim

This retained contract applies only when AI-Agent execution is separately admitted. It does not enable that execution or claim that its runtime implementation is present.

the Evaluation **must** verify independent execution through mock Agent end-to-end cases **and** the real DBOS queue.

## Details

### Scope

WORKFLOW_ORCHESTRATOR's initial local execution capability.

- queue a Run from a short-lived client, disconnect it, start a separate worker **and** verify recorded gather/check/fix results.
- verify clean checks, admitted fixes, blocked reports, Agent failure, timeout, duplicate requests **and** mismatched identities.
- verify worker restart acknowledges a previously applied after hash rather than repeating the edit.
- verify no recheck phase is introduced **and** initial findings remain **in** the saved report.
- distinguish mock execution from a live Codex model Run; mock passes prove integration boundaries, **not** semantic review quality.
