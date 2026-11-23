---
atom_family: SPEC
atom_id: AN-S-3578
container:
  component: C20
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 5
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Execute authorized Base Revise Runs independently

# Summary

Execute authorized Base Revise Runs independently

## Scope

WORKFLOW_ORCHESTRATOR's initial local execution capability.

## Claim

WORKFLOW_ORCHESTRATOR **must** execute an Operator-authorized RMED Atoms Base Revise Run independently of the requesting session.

## Details

- accept a stable Run ID, explicit Atom selection, current rule files, named Author, confidence threshold **and** permissions.
- execute gather, check **and** fix using the existing Action prompts **and** coordination Tool; preserve the initial checks **without** adding a recheck phase.
- return admission promptly. a separately started local worker executes queued Runs after the MCP client disconnects.
- report queued, running, completed, failed **or** interrupted execution honestly; provide saved status, results **and** recovery through existing observation capabilities.
- initial support is the existing RMED Atoms Base Revise Workflow. unknown Workflow definitions are explicit unsupported requests.
