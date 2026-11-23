---
atom_family: SPEC
atom_id: AN-S-3860
container:
  component: C20
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 18
  updated_at: 2026-09-23 04:20:00 +0400
---
## Summary

Render interconnected HTML graph views

# Render interconnected HTML graph views

the optional `GRAPH_UI` unit **must** render interconnected HTML graph views through `GRAPH_SERVER` from its current derived read model **and** the governed source frontier behind that model. It **may** also consume a persisted `GENERATE_ENTITY_GRAPH` Projection for declared Terms, their direct-parent tree, direct dependency graph, **and** complete dependency-Term closure. The views **must** provide short **and** detailed node presentation, tier, current Structural-unit, Content-role, **and** Type filters, orphan **and** cycle visibility controls, source lineage, unknown-region diagnostics, **and** access **to** current Atom content **without** treating **any** Projection as governed authority **or** modifying authority. Disabling or omitting `GRAPH_UI` **must not** disable `GRAPH_SERVER`, Tools, or MCP.
