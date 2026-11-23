---
atom_family: SPEC
atom_id: AN-S-4663
container:
  component: C9
tier: 3
context:
  template: action
  lens: DevOps
state:
  status: archived
  version: 9
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Wait for execution updates

# Summary

Wait for execution updates

## Operation

Execution notifications **means** the Programmatic Action implementing the following responsibility:

- compare snapshots of existing saved evidence; replay confirmed Journal updates after the cursor, await changes asynchronously, and distinguish unconfirmed event recording.
- accept the declared inputs **and** return the declared results under CA-D-517-WATCH_EXECUTION-ENG_DECISION--encode-watch-execution-tool-binding.
- report missing **or** ambiguous evidence as an explicit result.
- execution requires an Operator-authorized invocation; discovery **or** observation grants no mutation authority.

## Details

this Action provides the responsibility named by its Summary. a Workflow **may** invoke the Action through a Step. a direct call **may** use the same Action **without** creating a Workflow Run. observation preserves the original Run **and** evidence.
