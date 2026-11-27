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
  version: 26
  updated_at: "2026-11-27T17:35:01.150345+00:00"
---

## Summary

Delegate MCP calls to canonical Tools

## Claim

### Prose Claim

MCP maps Backend's JSON catalog to MCP Tools. For each invocation, it
forwards the Tool name, arguments, and request context. It returns the
Backend result or failure. Backend owns selection, validation, and
delegation to the canonical Tool.

**every** Finder **and** **every** Doer dry run **must** remain independently executable **without** MCP. A direct executable invocation of a ANECHOIC Markdown Atom Doer with `--apply` **must** reject the request **unless** it carries the authorized project-local MCP delegation **and** its sealed Initiative action envelope. Introducing MCP **must not** create a Tool dependency on MCP **or** another APPS unit.

## Details

MCP can read the Project Manifest and runtime settings through declared
interfaces for binding and startup.

Use the same Backend Tool definitions for catalog and dispatch. Preserve
Tool authority, failure behavior, and effect boundaries across transport.
