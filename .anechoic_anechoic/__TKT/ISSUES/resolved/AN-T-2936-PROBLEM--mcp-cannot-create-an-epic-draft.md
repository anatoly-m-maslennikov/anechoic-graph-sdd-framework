---
atom_family: TKT
atom_id: AN-T-2936
structure:
  container:
    component: C21
  priority: 2
context:
  template: problem
state:
  status: "resolved"
  version: 1
  updated_at: "2026-11-21T00:56:35.848051+00:00"
---

## Summary

MCP cannot create an Epic Draft

## Concern

The native `atom_lifecycle_create_draft` tool accepts `newAtom.template: task` only. A request with `newAtom.template: epic`, a valid Project container, and a Markdown body returns `invalid_input` for `newAtom`. AN-T-2935 had to be created directly on disk.

## Expected behavior

Create an Epic Draft through MCP and publish it through the normal lifecycle. Preserve existing Task Draft creation.
