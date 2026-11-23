---
atom_family: SPEC
atom_id: AN-S-1391
container:
  component: C21
tier: 1
context:
  lens: DES
state:
  status: "archived"
  version: 4
  updated_at: "2026-11-23T00:35:11.231439+00:00"
---

## Summary

MCP exposes the active Tool registry

## Claim

### Prose Claim

Backend publishes the enabled Tool catalog as JSON. Each entry supplies
the Tool name, description, and input schema. Backend uses the installed
Tool definitions for both the catalog and named dispatch. It applies
global and Project exclusions before publication and invocation.

MCP maps the catalog to MCP Tools. Report a missing or invalid catalog as
an explicit failure. For one admitted Project, use its enabled catalog.
For shared hosting, use the Backend coordinator's compatible catalog and
pass the explicit Project root on each call.
