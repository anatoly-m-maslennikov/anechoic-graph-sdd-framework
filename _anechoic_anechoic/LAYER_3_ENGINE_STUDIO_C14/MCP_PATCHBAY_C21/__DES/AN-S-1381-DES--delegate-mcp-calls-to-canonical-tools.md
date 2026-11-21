---
atom_family: SPEC
atom_id: AN-S-1381
structure:
  container:
    component: C21
  tier: 1
context:
  lens: DES
state:
  status: active
  version: 24
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Delegate MCP calls to canonical Tools

## Claim

### Prose Claim

**every** MCP Tool invocation **must** delegate **to** the selected canonical Tool executable **and** **must not** reimplement Tool decisions, project meaning, target resolution, validation, mutation, recovery behavior, **or** lifecycle semantics inside the MCP carrier. MCP owns **only** transport admission, canonical Tool selection, delegation, **and** result transport.

**every** Finder **and** **every** Doer dry run **must** remain independently executable **without** MCP. A direct executable invocation of a ANECHOIC Markdown Atom Doer with `--apply` **must** reject the request **unless** it carries the authorized project-local MCP delegation **and** its sealed Initiative action envelope. Introducing MCP **must not** create a Tool dependency on MCP **or** another APPS unit.

## Details

For an exposed validated Tool request, select the canonical Tool executable from the current registry, forward it without substituting MCP behavior, and transport the Tool result with every failure and side-effect boundary. Stop when canonical selection, request validation, or delegated execution fails.
