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
  version: 12
  updated_at: 2026-11-05 13:04:02 +0400
---
## Summary

Find Tools by capability

# Summary

Find Tools by capability

## Operation

Tool discovery **means** the Programmatic Action implementing the following responsibility:

- for a non-empty request, search declared Tool bindings and observed entrypoints; keep implemented, MCP-exposed, source-only, missing, and unresolved bindings distinct.
- accept the declared inputs **and** return the declared results under CA-D-512-DISCOVER_TOOLS-ENG_DECISION--encode-discover-tools-tool-binding.
- report missing **or** ambiguous evidence as an explicit result.
- execution requires an Operator-authorized invocation; discovery **or** observation grants no mutation authority.

## Details

this Action provides the responsibility named by its Summary. a Workflow **may** invoke the Action through a Step. a direct call **may** use the same Action **without** creating a Workflow Run. observation preserves the original Run **and** evidence.

With an empty request, return the generated released-MCP root catalog under its declared root/groups contract. With a non-empty request, retain the source-binding search and its existing filters and result contract. Reading the catalog grants no execution or mutation authority.
