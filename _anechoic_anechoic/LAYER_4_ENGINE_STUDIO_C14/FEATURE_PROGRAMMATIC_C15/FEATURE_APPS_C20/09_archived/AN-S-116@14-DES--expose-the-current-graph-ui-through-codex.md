---
atom_family: SPEC
atom_id: AN-S-116
container:
  component: C20
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 14
  updated_at: 2026-10-24 01:28:26 +0400
---
## Summary

Expose the current GRAPH_UI through Codex

# Expose the current GRAPH_UI through Codex

`CODEX_PLUGIN` **must** let a Codex operator open **and** navigate the current `GRAPH_UI`, apply its governed filters, select graph nodes, **and** inspect their current source content, paths, digests, **and** provenance **without** copying the graph read model into plugin authority. The plugin **must** consume the GRAPH_UI's read-only interface, preserve stale **or** unavailable-source states, **and** **must not** mutate an Atom, Journal, Projection, graph source, **or** derived GRAPH_UI state through the viewing path.
