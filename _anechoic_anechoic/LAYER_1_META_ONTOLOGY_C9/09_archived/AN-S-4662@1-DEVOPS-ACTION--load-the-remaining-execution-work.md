---
atom_family: SPEC
atom_id: AN-S-4662
container:
  component: C9
tier: 4
context:
  template: action
  lens: DevOps
state:
  status: archived
  version: 1
  updated_at: 2026-10-03 14:55:01 +0000
---
## Summary

Load the remaining execution work

# Summary

Load the remaining execution work

## Operation

Execution continuation context **means** the Programmatic Action implementing the following responsibility:

- derive remaining work from the saved initial checks and correction dispositions; compare source and criteria fingerprints and report drift before continuation.
- accept the declared inputs **and** return the declared results under CA-D-516-RESUME_EXECUTION_CONTEXT--encode-resume-execution-context-bindings.
- report missing **or** ambiguous evidence as an explicit result.
- execution requires an Operator-authorized invocation; discovery **or** observation grants no mutation authority.

## Details

this Action provides the responsibility named by its Summary. a Workflow **may** invoke the Action through a Step. a direct call **may** use the same Action **without** creating a Workflow Run. observation preserves the original Run **and** evidence.
