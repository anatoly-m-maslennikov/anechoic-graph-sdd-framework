---
atom_family: TKT
atom_id: AN-T-1835
structure:
  container:
    atom: AN-T-1846
  priority: 2
context:
  template: work_report
state:
  status: done
  version: 1
  updated_at: 2026-11-09 00:18:04 +0400
---

## Summary

Fix relation materialization with the generated registry

## Details

Canonical direct facts and derived inverse facts share one registry. Native GRAPH_TABLE checks verified both directions for the APPS, PROGRAMMATIC and Workbench containment chain. Header Container supplies direct ownership facts. Ambiguous case-colliding names are warned about and omitted.
