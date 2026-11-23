---
atom_family: SPEC
atom_id: AN-S-4411
container:
  component: C20
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 31
  updated_at: 2026-11-10 11:12:30 +0400
---
## Summary

Render interconnected HTML graph views

## Claim

### Prose Claim

The optional `GRAPH_UI` unit **must** render interconnected HTML graph views through `WORKBENCH` from its current derived read model **and** the governed source frontier behind that model.

It **may** also consume a persisted `GENERATE_ENTITY_GRAPH` Projection for declared Terms, their direct-parent tree, direct dependency graph **and** complete dependency-Term closure.

The views **must** provide:

- short **and** detailed node presentation;
- Tier, Scope Unit, Role **and** Form filters;
- orphan **and** cycle visibility controls;
- source lineage;
- unknown-region diagnostics; **and**
- access to current Atom content.

The views **must not** treat any Projection as governed authority or modify authority. Disabling or omitting `GRAPH_UI` **must not** disable `WORKBENCH`, Tools or MCP.
