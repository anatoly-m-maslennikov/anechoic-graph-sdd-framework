---
atom_family: SPEC
atom_id: AN-S-3886
container:
  component: C21
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 7
  updated_at: 2026-10-24 00:28:02 +0400
---
## Summary

Reject one stale MCP project frontier

# Reject one stale MCP project frontier

## Claim checked

An MCP invocation **must** bind **to** one current project, installed release, graph frontier, **and** registry revision.

## Test case

Invoke one Tool through a registry made stale by a changed project frontier.

## Acceptance criteria

MCP rejects the invocation explicitly **and** exposes enough provenance **to** identify the stale boundary.

## Failure disposition

Stop **before** Tool execution; do **not** guess a current release **or** project root.
