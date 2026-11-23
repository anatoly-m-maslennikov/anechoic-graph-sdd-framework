---
atom_family: SPEC
atom_id: AN-S-3722
container:
  component: C20
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 4
  updated_at: 2026-10-23 23:34:06 +0400
---
## Summary

Carry coverage gate and Operator question results

# Summary

Carry coverage gate and Operator question results

## Scope

RMED Atoms Base Revise execution in WORKFLOW_ORCHESTRATOR.

## Claim

Coverage Gate results **must** carry the following evidence fields.

## Details

- phase, expected, covered, missing, coverage_percent, result **and** operator_question.
- result: covered **or** ask_operator. unknown accounting has coverage_percent=null, **not** **`=100`**.
- Run status includes coverage_gates **and** operator_question. a failed gate sets outcome=interrupted **and** leaves completed work intact.
- full reports include a Coverage Gates section; confirmed gate events use the existing shared Project Journal.
- Workflow gate Action: CA-O-118; phase substeps: CA-O-119, CA-O-120, CA-O-121.
