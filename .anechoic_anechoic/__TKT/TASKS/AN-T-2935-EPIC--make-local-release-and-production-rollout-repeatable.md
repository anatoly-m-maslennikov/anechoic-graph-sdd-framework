---
atom_family: TKT
atom_id: AN-T-2935
structure:
  container:
    component: C00
  priority: 2
context:
  template: epic
state:
  status: "active"
  version: 1
  updated_at: "2026-11-20T19:49:44.161937+00:00"
---

## Summary

Make Local Release and production rollout repeatable

## Objective

Replace recurring ad hoc release scripts with maintained tools in `LAYER_5_FRAMEWORK_DELIVERY`.

## Scope

- Review recent release scripts and reuse the existing `release.py` workflow where it fits.
- Keep the recurring steps for isolated verification, verified build promotion, and rollback. Document how to run them.

## Done when

One isolated rehearsal uses the maintained tools to verify a release, promote the verified build, and restore the previous build.
