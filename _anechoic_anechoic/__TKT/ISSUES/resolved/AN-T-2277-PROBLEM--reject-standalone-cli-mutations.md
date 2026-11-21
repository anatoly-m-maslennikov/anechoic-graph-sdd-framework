---
atom_family: TKT
atom_id: AN-T-2277
structure:
  container:
    component: C16
  priority: 2
context:
  template: problem
state:
  status: resolved
  version: 2
  updated_at: 2026-10-23 03:14:50 +0400
---
# Summary

Reject standalone CLI mutations

## Concern

the canonical Atom Create and Update CLI entrypoints expose direct apply while current authority requires sealed MCP delegation.

## Evidences

the final source-to-code review confirmed this bounded discrepancy. independent adjudication separated it from unsupported status-transition and authorization-model proposals. focused fixture results establish repair behavior, not actual release completion.

## Blast radius

the affected selected capability and its current release candidate. installed N, historical Events and frozen test snapshots remain preserved.

## Decision

reject standalone CLI apply before writes, preserving preview and the existing admitted selected/MCP native mutation functions.

## Result

the canonical executable wrappers refuse standalone apply before repository resolution and writes. the 26-test focused suite passes, including actual subprocess refusal and preview zero-write checks; independent source/code review accepts the bounded repair. this resolves the bounded code discrepancy; it is not evidence of actual release promotion.
