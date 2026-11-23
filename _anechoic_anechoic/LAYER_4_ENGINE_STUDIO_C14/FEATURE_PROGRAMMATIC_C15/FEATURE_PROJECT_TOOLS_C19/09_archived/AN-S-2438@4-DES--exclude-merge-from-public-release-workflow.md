---
atom_family: SPEC
atom_id: AN-S-2438
container:
  component: C19
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 4
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Exclude merge from public-release Workflow

# Summary

Exclude merge from public-release Workflow

## Scope

one public-release Workflow execution.

## Claim

**the Operator** **must not** merge, approve, retarget, or otherwise adopt the public PR through this Workflow.

## Details

The terminal public result is an actual open or updated PR with evidence, not a release merge, protected-branch update, tag, or deployment.
