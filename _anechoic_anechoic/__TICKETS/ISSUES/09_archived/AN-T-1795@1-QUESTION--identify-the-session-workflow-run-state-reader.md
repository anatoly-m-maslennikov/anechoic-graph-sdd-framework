---
atom_family: TKT
atom_id: AN-T-1795
container:
  component: C14
priority: 2
context:
  template: question
state:
  status: archived
  version: 1
  updated_at: 2026-11-11 00:22:28 +0400
---

## Summary

Identify the session Workflow Run state reader

## Concern

R3016 requires Project/session-isolated active Run lists and recorded history. The installed provider inventory is Workbench-only, and initial PROGRAMMATIC inspection found no retained generic executor or Run-state reader. The legacy Journal library writes records but supplies no generic reader; release events currently use Run IDs as session IDs and cannot establish client-session ownership.

Do not invent an empty successful result or a parallel Run store. Identify an admitted state/history owner, or explicitly defer the read capability while implementing the independent generic caller context and hook. The Operator question is pending; broad source investigation continues.
