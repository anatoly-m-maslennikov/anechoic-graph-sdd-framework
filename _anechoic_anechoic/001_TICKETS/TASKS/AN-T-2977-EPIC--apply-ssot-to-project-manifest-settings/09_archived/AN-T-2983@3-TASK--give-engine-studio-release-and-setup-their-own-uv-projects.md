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
  version: 3
  updated_at: "2026-11-22T10:32:28.953480+00:00"
---

## Summary

Give Engine Studio Release and Setup their own uv Projects

## Objective

Give Engine Studio, Release, and Setup one Python root and one virtual
development environment each. Launch executables through uv in the owning
Project.
Cross-child calls use the callee's CLI or API. Follow AN-S-3310@2.

## Done when

Use one lock per child. Select the QA dependency group for tests, Ruff,
and mypy where needed. Use runtime dependencies for deployed environments.
Release invokes Engine Studio tests in the Engine Studio QA environment.

Verify each child's executable with its own uv Project and environment.
Verify that packaged Engine Studio starts and serves a query with the
runtime dependencies, with Ruff and mypy absent. Preserve the
previous-image release path.
