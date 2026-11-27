---
atom_family: SPEC
atom_id: AN-S-5173
container:
  component: C21
tier: 1
context:
  lens: DES
state:
  status: active
  version: 1
  updated_at: '2026-11-27T17:35:02.219595+00:00'
---

## Summary

Preserve the standalone Finder and Doer invocation boundary

## Claim

**every** Finder **and** **every** Doer dry run **must** remain independently executable **without** MCP. A direct executable invocation of a ANECHOIC Markdown Atom Doer with `--apply` **must** reject the request **unless** it carries the authorized project-local MCP delegation **and** its sealed Initiative action envelope. Introducing MCP **must not** create a Tool dependency on MCP **or** another APPS unit.
