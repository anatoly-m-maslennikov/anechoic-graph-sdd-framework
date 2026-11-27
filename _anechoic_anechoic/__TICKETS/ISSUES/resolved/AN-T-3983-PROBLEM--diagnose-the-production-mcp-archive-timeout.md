---
atom_family: TKT
atom_id: AN-T-3983
concern:
- subject: C68
  path: Project Structure.components
  relation: affects
container:
  component: C68
priority: 2
context:
  template: problem
state:
  status: resolved
  version: 1
  updated_at: '2026-11-26T10:01:14Z'
---

## Summary

Diagnose the production MCP archive timeout

## Claim

### Prose Claim

On Studio 0.4.4.76, the MCP client stopped waiting after 300 seconds for `atom_lifecycle_change_status` to archive `AN-S-1798@33`. Production served reads and still showed Active. A separate file repair archived the revision. Production MCP later indexed it as Archived.

The old route selected full Project capture for this prose Spec because of its C9 `_DES` path. A disposable replay of the old Archive route failed before the write when the cold Worker could not bind the Project Manifest. The production logs show competing generation failures during the request. They do not show which server phase consumed the five minutes.

## Resolution criteria

Reproduce the request on a disposable copy of the full Project and identify the stalled phase. An eligible exact revision archives successfully and appears in the index. An ineligible revision returns an explicit error and leaves the source intact.

## Resolution

Use indexed capture when archiving a plain DES Spec. Keep full capture for Model declarations. The archive writer checks the canonical path against the live Header before writing.

On a disposable Project with 53,746 Atoms, the original status-change call archived `AN-S-1798@33` in 20.56 seconds. MCP returned the exact Archived revision and the body stayed intact. A stale Version returned `source_changed` with no file effects. The fix awaits deployment.
