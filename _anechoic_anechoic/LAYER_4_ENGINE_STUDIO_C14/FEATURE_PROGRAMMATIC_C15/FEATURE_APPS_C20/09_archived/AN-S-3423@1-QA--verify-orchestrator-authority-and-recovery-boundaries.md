---
atom_family: SPEC
atom_id: AN-S-3423
container:
  component: C20
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: 2026-10-04 02:57:00 +0400
---
## Summary

Verify orchestrator authority and recovery boundaries

# Summary

Verify orchestrator authority and recovery boundaries

## Scope

WORKFLOW_ORCHESTRATOR's initial local execution capability.

## Claim

the Evaluation **must** verify rejection of orchestration requests **or** Agent output outside declared authority.

## Details

- reject unsupported Workflows, traversal, symlinks, protected paths, unknown fields, stale input **and** conflicting duplicate Run requests.
- check phases cannot modify source Atoms; allow_fixes=false preserves source bytes.
- reject changed Atom ID **or** Summary, low confidence, incomplete checks **and** invalid report fields.
- record uncertainty **after** dispatch intent with no accepted output, **without** silently rerunning the Agent.
- verify failure **and** interruption remain observable through status, shared Journal **and** full reports.
