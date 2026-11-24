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
  status: backlog
  version: 4
  updated_at: "2026-11-22T17:07:14.791641+00:00"
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

A full-project Docker canary built a fresh DuckDB index and started
on AN-S-3037@19. Both MCP release commands returned the host uv
commands. The 4 KiB result limit and DuckDB storage passed again.
The read, capture, Structure, and startup tests passed (40 tests).

The first Local Release stopped at its Git checkpoint because the
checkout changed during validation. The isolated release passed static
QA and exposed Beta API and MCP failures in the checkpointed inputs.
Verify the installed runtime after a full Local Release passes.
