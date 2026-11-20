---
atom_family: TKT
atom_id: AN-T-2163
structure:
  container:
    atom: AN-T-2078
  priority: 2
context:
  template: work_report
state:
  status: canceled
  version: 1
  updated_at: 2026-11-11 15:21:04 +0400
---

## Summary

Implement the new Atom Lifecycle Tools

## Details

Implemented Plan Archive for a verified containment tree with no older Atom Markdown to move. Each current Plan is archived child-first into the shared archive, and matching asset directories are verified before removal.

The staged MCP gateway archived a three-level tree and preserved a prior archive and attached assets. A separate failure check verified completed effects and the remaining target. Folder-backed Status changes and Workflow archive placement remain open in CA-C-730.
