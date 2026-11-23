---
atom_family: SPEC
atom_id: AN-S-1381
container:
  component: C21
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 21
  updated_at: 2026-10-27 19:59:50 +0400
---
## Summary

Delegate MCP calls to canonical Tools

# Delegate MCP calls to canonical Tools

**every** MCP invocation **must** delegate **to** the selected canonical Tool executable **and** **must not** reimplement Tool decisions, project meaning, target resolution, validation, mutation, recovery behavior, **or** lifecycle semantics inside the MCP carrier. MCP owns **only** transport admission, canonical Tool selection, delegation, **and** result transport.

**every** Finder **and** **every** Doer dry run **must** remain independently executable **without** MCP. A direct executable invocation of a ANECHOIC Markdown Atom Doer with `--apply` **must** reject the request **unless** it carries the authorized project-local MCP delegation **and** its sealed Initiative action envelope. Introducing MCP **must not** create a Tool dependency on MCP **or** another APPS unit.
