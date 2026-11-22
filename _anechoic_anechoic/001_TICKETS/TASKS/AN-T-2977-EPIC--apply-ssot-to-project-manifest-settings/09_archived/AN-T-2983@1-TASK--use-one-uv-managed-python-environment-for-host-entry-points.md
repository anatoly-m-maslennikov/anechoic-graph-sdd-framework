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
  version: 1
  updated_at: "2026-11-22T10:24:01.043150+00:00"
---

## Summary

Use one uv-managed Python environment for host entry points

## Objective

Run Python with uv and use one virtual environment. Make Setup, Release,
MCP launchers, and tests share the selected host environment. Preserve the
image's own uv-managed environment for Docker.

## Done when

Verify commands from the checkout and a selected installed package. Confirm
that launchers and workers use the intended interpreter and no duplicate
host environment is created during setup, test, launch, or release.
This check precedes the one-root cutover in AN-T-2980.
