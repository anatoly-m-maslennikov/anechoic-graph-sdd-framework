---
atom_family: TKT
atom_id: AN-T-2169
container:
  atom: AN-T-2078
priority: 2
context:
  template: work_report
state:
  status: canceled
  version: 1
  updated_at: 2026-11-11 17:17:22 +0400
---

## Summary

Implement the new Atom Lifecycle Tools

## Details

Deployed the retained-history fix. Disposable MCP HTTP calls closed a parent Plan, canceled its active child, and archived the resulting tree. Both moves preserved an older Archived revision byte-for-byte. The older revision was never a Status target.

The Model projection CLI rendered 71 distinct Aspect memberships from the five pinned Formal Claim previews, preserving full paths without Main Subject fallback. The 164 graph tests and 81 lifecycle tests passed. CA-C-730 still tracks formal authoring admission, reopening terminal trees and folder-backed Update.
