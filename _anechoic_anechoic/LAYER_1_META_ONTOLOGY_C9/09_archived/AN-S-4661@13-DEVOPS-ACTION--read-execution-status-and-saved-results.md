---
atom_family: SPEC
atom_id: AN-S-4661
container:
  component: C9
tier: 3
context:
  template: action
  lens: DevOps
state:
  status: archived
  version: 13
  updated_at: 2026-10-27 19:59:46 +0400
---
## Summary

Read execution status and saved results

# Summary

Read execution status and saved results

## Operation

Execution observation **means** the Programmatic Action implementing the following responsibility:

- read the existing Run backend and saved reports; retain Action-to-Step correlation and never infer completion from an applied correction.
- accept the declared inputs **and** return the declared results under CA-D-515-GET_EXECUTION_STATUS-ENG_DECISION--encode-get-execution-status-tool-binding.
- report missing **or** ambiguous evidence as an explicit result.
- execution requires an Operator-authorized invocation; discovery **or** observation grants no mutation authority.

## Details

this Action provides the responsibility named by its Summary. a Workflow **may** invoke the Action through a Step. a direct call **may** use the same Action **without** creating a Workflow Run. observation preserves the original Run **and** evidence.
