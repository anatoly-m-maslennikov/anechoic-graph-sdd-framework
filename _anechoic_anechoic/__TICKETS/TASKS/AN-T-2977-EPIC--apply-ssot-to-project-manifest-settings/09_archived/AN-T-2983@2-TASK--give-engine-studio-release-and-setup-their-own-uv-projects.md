---
atom_family: TKT
atom_id: AN-T-2983
container:
  atom: AN-T-2977
priority: 2
context:
  template: task
  label: Task
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-22T10:29:51.120297+00:00"
---

## Summary

Give Engine Studio Release and Setup their own uv Projects

## Objective

Give Engine Studio, Release, and Setup one Python root and one virtual
environment each. Launch their executables through uv in the owning Project.
Cross-child calls use the callee's CLI or API. Follow AN-S-3310@1.

## Done when

Verify Setup, Release, and Engine Studio executables with each child's
uv Project and virtual environment. Release invokes Engine Studio tests
in the Engine Studio environment. Verify the packaged Engine Studio image
and preserve the previous-image release path.
