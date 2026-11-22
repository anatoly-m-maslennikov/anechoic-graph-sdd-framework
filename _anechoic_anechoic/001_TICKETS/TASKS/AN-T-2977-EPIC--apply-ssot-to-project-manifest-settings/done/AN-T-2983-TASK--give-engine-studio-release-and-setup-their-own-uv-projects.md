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
  status: "done"
  version: 5
  updated_at: "2026-11-22T11:06:18.595706+00:00"
---

## Summary

Give Engine Studio Release and Setup their own uv Projects

## Objective

Give Engine Studio, Release, and Setup one Python root and one lock each.
Launch executables through uv in the owning Project. Cross-child calls
use the callee's CLI or API. Follow AN-S-3310@4.

## Done when

Verify the `release` and `setup` executables in their own environments.
Run Engine Studio tests and static analysis in `dev`. Verify the image
starts and serves a query in `prod` with Ruff and mypy absent. Build both
Engine Studio environments from the same lock. Preserve the previous-image
release path.

## Verification

Release and Setup have separate uv Projects and locks. Engine prod and dev share one lock. Setup and Release invoke other children through their executable interfaces. All 384 functional tests and three disposable Docker checks passed. The image excludes Ruff and mypy.
