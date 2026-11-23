---
atom_family: SPEC
atom_id: AN-S-1384
container:
  component: C21
tier: 4
context:
  lens: DES
state:
  status: archived
  version: 11
  updated_at: 2026-10-21 20:27:48 +0000
---
## Summary

Bind MCP operation to the current project frontier

# Bind MCP operation to the current project frontier

A legacy one-Project MCP service instance **must** bind **to** exactly one
resolved ANECHOIC Project root, selected installed Tool release, current
project-graph frontier, **and** generated MCP registry revision. In the shared
service, native Tool execution and invocation **must** bind **to** exactly one
validated Project identity and frontier. Host-scoped Tool discovery **may**
publish the initial union of compatible Project frontiers, with per-Project
source and revision provenance; the union is not a selected Project and must
not be treated as one. Discovery **and** results **must** expose sufficient
source **and** revision provenance **to** diagnose currentness; cross-project
path escape, unresolved project identity, **and** invocation through a stale
registry **must** fail explicitly.

Scope check: the legacy launcher’s service instance remains one-Project. The
shared service’s host-scoped discovery union is not a selected Project; every
native execution/invocation remains bound to one validated Project
identity/frontier.
