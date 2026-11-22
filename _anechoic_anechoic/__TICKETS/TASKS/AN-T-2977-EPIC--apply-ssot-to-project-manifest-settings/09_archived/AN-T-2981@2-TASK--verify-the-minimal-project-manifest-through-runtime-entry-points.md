---
atom_family: TKT
atom_id: AN-T-2981
container:
  atom: AN-T-2977
priority: 2
context:
  template: task
  label: Task
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-22T16:34:52.768906+00:00"
---

## Summary

Verify the minimal Project Manifest through runtime entry points

## Objective

Validate Project selection, compiled Model and Structure, Workbench storage and queries, MCP release access, and the inferred Import Graph roots. Record the effective settings and regression results.

## Verification

The checkout selects AN-S-3037@17 and compiles the Model and 50 Components. Disposable MCP and Workbench checks passed. Verify the installed runtime after Local Release.
