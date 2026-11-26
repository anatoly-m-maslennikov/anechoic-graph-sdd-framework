---
atom_family: SPEC
atom_id: AN-S-4659
container:
  component: C9
tier: 3
context:
  template: action
  lens: DevOps
state:
  status: archived
  version: 7
  updated_at: 2026-10-24 01:18:03 +0400
---
## Summary

Find Workflows and Actions by outcome

# Summary

Find Workflows and Actions by outcome

## Operation

Workflow and Action discovery **means** the Programmatic Action implementing the following responsibility:

- search carried Operations Type, Summary, Operation, Scope Unit, and declared implementation bindings; report unknown execution kind explicitly.
- accept the declared inputs **and** return the declared results under CA-D-513-DISCOVER_OPERATIONS--encode-discover-operations-bindings.
- report missing **or** ambiguous evidence as an explicit result.
- execution requires an Operator-authorized invocation; discovery **or** observation grants no mutation authority.

## Details

this Action provides the responsibility named by its Summary. a Workflow **may** invoke the Action through a Step. a direct call **may** use the same Action **without** creating a Workflow Run. observation preserves the original Run **and** evidence.
