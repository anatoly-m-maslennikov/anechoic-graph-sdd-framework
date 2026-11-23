---
atom_family: SPEC
atom_id: AN-S-4658
container:
  component: C9
tier: 3
context:
  template: action
  lens: DevOps
state:
  status: archived
  version: 4
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Find Tools by capability

# Summary

Find Tools by capability

## Operation

Tool discovery **means** the Programmatic Action implementing the following responsibility:

- search declared Tool bindings and observed entrypoints; keep implemented, MCP-exposed, source-only, missing, and unresolved bindings distinct.
- accept the declared inputs **and** return the declared results under CA-D-512-DISCOVER_TOOLS--encode-discover-tools-bindings.
- report missing **or** ambiguous evidence as an explicit result.
- execution requires an Operator-authorized invocation; discovery **or** observation grants no mutation authority.

## Details

this Action provides the responsibility named by its Summary. a Workflow **may** invoke the Action through a Step. a direct call **may** use the same Action **without** creating a Workflow Run. observation preserves the original Run **and** evidence.
