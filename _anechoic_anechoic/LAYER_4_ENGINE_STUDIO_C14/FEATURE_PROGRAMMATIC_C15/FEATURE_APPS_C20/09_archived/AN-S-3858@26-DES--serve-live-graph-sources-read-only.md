---
atom_family: SPEC
atom_id: AN-S-3858
container:
  component: C20
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 26
  updated_at: 2026-10-27 19:59:50 +0400
---
## Summary

Serve live graph sources read-only

# Serve live graph sources read-only

the headless `GRAPH_SERVER` unit **must** give Tools, MCP clients, **and** optional interfaces strictly read-only access **to** registered current Atoms, Journals, Projections, **and** derived graph data, including persisted `GENERATE_ENTITY_GRAPH` Projection carriers; return source kind, non-authoritative status, source-frontier lineage, raw content, canonical path, **and** current digest **where** applicable; operate without `GRAPH_UI`; **and** reject inactive **or** unregistered targets, path traversal, symlink escape, authority substitution, **and** **every** mutation.
