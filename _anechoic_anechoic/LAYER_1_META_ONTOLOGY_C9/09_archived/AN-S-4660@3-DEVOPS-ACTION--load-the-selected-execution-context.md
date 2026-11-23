---
atom_family: SPEC
atom_id: AN-S-4660
container:
  component: C9
tier: 3
context:
  template: action
  lens: DevOps
state:
  status: archived
  version: 3
  updated_at: 2026-10-23 03:06:32 +0400
---
## Summary

Load the selected execution context

# Summary

Load the selected execution context

## Operation

Execution context retrieval **means** the Programmatic Action implementing the following responsibility:

- resolve exact identifiers; load the selected definition and directly related Step or Action definitions, relevant bound prompts, and applicable RMED from declared Scope Unit ancestry.
- accept the declared inputs **and** return the declared results under CA-D-514-GET_EXECUTION_CONTEXT--encode-get-execution-context-bindings.
- report missing **or** ambiguous evidence as an explicit result.
- execution requires an Operator-authorized invocation; discovery **or** observation grants no mutation authority.

## Details

this Action provides the responsibility named by its Summary. a Workflow **may** invoke the Action through a Step. a direct call **may** use the same Action **without** creating a Workflow Run. observation preserves the original Run **and** evidence.
