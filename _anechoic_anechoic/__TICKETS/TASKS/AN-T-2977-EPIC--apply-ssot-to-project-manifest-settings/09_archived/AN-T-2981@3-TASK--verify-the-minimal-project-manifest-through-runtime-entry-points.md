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
  version: 3
  updated_at: "2026-11-22T17:07:14.790397+00:00"
---

## Summary

Verify the minimal Project Manifest through runtime entry points

## Objective

Validate Project selection, compiled Model and Structure, Workbench storage and queries, MCP release access, and the inferred Import Graph roots. Record the effective settings and regression results.

## Verification

The checkout selects AN-S-3037@17 and compiles the Model and 50 Components. Disposable MCP and Workbench checks passed. Verify the installed runtime after Local Release.

The checkout selects AN-S-3037@19 and compiles 116 Model declarations,
56 Components, and 6 Component Seeds. Project selection uses the
underscore control root. Import Graph infers the Engine Studio, Release,
and Setup roots.

The smaller canary reused its DuckDB projection after restart and queried
the Journal table. It returned the host uv commands for both release
Workflows. A 4,000-byte CSV value stayed inline and a 4,200-byte value
went to a file. Static QA and 36 focused checks passed.

The full-project canary timed out before Workbench became ready.
The Model and Structure compiled in both launch attempts. A later
diagnostic run also hit the compiler deadline. Verify the installed
runtime after a Local Release passes. Live MCP still reports AN-S-3037@16.
