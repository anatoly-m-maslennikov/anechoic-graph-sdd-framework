---
atom_family: TKT
atom_id: AN-T-2130
structure:
  container:
    atom: AN-T-2078
  priority: 2
context:
  template: work_report
state:
  status: done
  version: 1
  updated_at: 2026-11-11 07:29:57 +0400
---

## Summary

Verify rebuilt Workbench image

## Details

The 87f745f425bc image loaded schema v2, served the frontend, returned seven declared Content columns and exposed three native Formal Claims. HTTP and MCP both accepted a graph query ending in a line comment and returned the expected uncapped and preview results. All six changed backend module hashes match the build context.

Scope refresh memory and two-image declaration acceptance remain open. Evidence: `.anechoic_tmp/CA-P-2791/CA-P-2866/formal-input-20261111/image-build-ancestry-v2/`.
