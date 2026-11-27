---
atom_family: SPEC
atom_id: AN-S-1381
container:
  component: C21
tier: 1
context:
  lens: DES
state:
  status: active
  version: 27
  updated_at: "2026-11-27T17:35:01.150345+00:00"
---

## Summary

Delegate MCP calls to canonical Tools

## Claim

### Prose Claim

MCP maps Backend's JSON catalog to MCP Tools. Forward admitted calls under AN-S-3366. Backend owns Tool selection, validation, and dispatch under AN-S-1384.

Apply AN-S-5173 to direct Tool invocation.

## Details

MCP can read the Project Manifest and runtime settings through declared
interfaces for binding and startup.

Use the same Backend Tool definitions for catalog and dispatch. Preserve
Tool authority, failure behavior, and effect boundaries across transport.
