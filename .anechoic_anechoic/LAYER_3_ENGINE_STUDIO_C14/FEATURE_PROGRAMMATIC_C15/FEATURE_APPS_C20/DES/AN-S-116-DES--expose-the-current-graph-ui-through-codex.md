---
identity:
  atom_id: AN-S-116
context:
  container:
    component: C20
  tier: 1
  lens: DES
state:
  status: active
  version: 24
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Expose the current GRAPH_UI through Codex

# Expose the current GRAPH_UI through Codex

`CODEX_PLUGIN` **must** let a Codex operator open **and** navigate the current `GRAPH_UI`, apply its governed filters, select graph nodes, **and** inspect their current source content, paths, digests, **and** provenance **without** copying the graph read model into plugin authority. The plugin **must** consume the GRAPH_UI's read-only interface, preserve stale **or** unavailable-source states, **and** **must not** mutate an Atom, Journal, Projection, graph source, **or** derived GRAPH_UI state through the viewing path.
