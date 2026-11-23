---
atom_family: SPEC
atom_id: AN-S-3983
container:
  component: C20
tier: 4
context:
  lens: DevOps
state:
  status: archived
  version: 8
  updated_at: 2026-09-23 04:25:00 +0400
---
## Summary

Deliver the Requirement Projection browser locally

# Deliver the Requirement Projection browser locally

the optional GRAPH_UI Requirement Projection browser **must** be delivered as exactly one project-local, non-authoritative `.anechoic/mrt_atoms.html` file with embedded JavaScript, backed by strictly read-only `GRAPH_SERVER` access **to** the current per-structural-unit Requirement STG files **and** actual Atom Markdown; this Delivery creates no sibling web assets, is not required for headless service, **and** does **not** publish, host, **or** distribute the MRT outside the project.
