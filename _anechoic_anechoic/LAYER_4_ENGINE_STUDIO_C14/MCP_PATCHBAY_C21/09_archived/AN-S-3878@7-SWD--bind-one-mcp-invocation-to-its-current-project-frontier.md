---
atom_family: SPEC
atom_id: AN-S-3878
container:
  component: C21
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 7
  updated_at: 2026-10-21 20:16:45 +0000
---
## Summary

Bind one MCP invocation to its current project frontier

# Bind one MCP invocation to its current project frontier

## Applicable when

Apply **when** an MCP service instance discovers **or** invokes an exposed Tool.

## Procedure

1. Resolve exactly one explicit Project identity, project root, selected
   installed Tool release, project-graph frontier, **and** MCP registry
   revision for each call.
2. Include sufficient source **and** revision provenance **in** discovery
   **and** result records; carry the outer project root only at the native
   request schema root while preserving the native request and result.
3. Reject cross-project path escape, unresolved identity, **or** a stale registry **before** Tool invocation.

## Outcome

**every** MCP operation is attributable **to** one current Project **and** Tool
frontier, even when one shared service publishes a union of valid Project
frontiers.

## Failure or stop

Stop at an unresolved **or** stale frontier; do **not** guess a project **or** release.
