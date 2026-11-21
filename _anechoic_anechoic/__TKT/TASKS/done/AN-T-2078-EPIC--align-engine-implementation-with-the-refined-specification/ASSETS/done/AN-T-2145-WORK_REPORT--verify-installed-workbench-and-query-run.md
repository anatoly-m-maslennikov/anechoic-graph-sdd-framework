---
atom_family: TKT
atom_id: AN-T-2145
structure:
  container:
    atom: AN-T-2078
  priority: 2
context:
  template: work_report
state:
  status: done
  version: 1
  updated_at: 2026-11-11 08:51:05 +0400
---

## Summary

Verify installed Workbench and query_run

## Details

Local Release installed Workbench 0.4.4.43 as image `sha256:1d89cc9b99869d1fc4d42c38cd0bf7790c1bad4a7098a3ceb3bcd640a1b2fb60`. Focused validation ran 64 modules and 566 cases, with two skips and no failed modules.

The installed HTTP and MCP query_run interfaces agree on seven declared Content columns, three native Formal Claims, and both directions of containment. query_run also lists all five Methodology Scope Units. The release removed the superseded Project-owned container and three obsolete Project-owned images. Its receipt retains cleanup pending for images without verified ownership.

The release receipt is `.anechoic_runtime/simple_local_release/reports/engine-refinement-20261111-v5.md`. Installed proof is in `.anechoic_tmp/CA-P-2791/CA-P-2818/installed-acceptance-v5.json`.
