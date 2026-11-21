---
atom_family: TKT
atom_id: AN-T-2138
structure:
  container:
    atom: AN-T-2078
  priority: 2
context:
  template: work_report
state:
  status: done
  version: 1
  updated_at: 2026-11-11 07:57:14 +0400
---

## Summary

Verify Workbench release inputs

## Details

Recompiled the schema and canonical relation registry from the current checkout. The schema modes and relation registry match the tested image. Schema input provenance changed. All 175 Engine Python modules from the tested build have matching executable syntax.

The installed Workbench served its page but lacked the declared Content columns. The post-release check now covers those columns, native Declarations and both containment directions through Workbench HTTP and MCP query_run. The assets and check are in `.anechoic_tmp/CA-P-2791/CA-P-2818/`.
