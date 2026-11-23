---
atom_family: TKT
atom_id: AN-T-2204
container:
  atom: AN-T-2078
priority: 2
context:
  template: work_report
state:
  status: archived
  version: 1
  updated_at: '2026-11-12T02:41:19.578333+00:00'
---
## Summary

Fix lifecycle operations on Epic trees

## Details

Verified through MCP in a disposable Project. Changing an Epic from Backlog to Active activated a direct and a nested Current Task. A separate Epic with a Draft child became Active, with the child remaining Draft. A content-only Update created the next Epic Version and preserved both Current children.

Verified image `sha256:7607f7793de81d53b1d68b31c49ebe97c5dde9d2214b2318b44142dec92599f1`.
