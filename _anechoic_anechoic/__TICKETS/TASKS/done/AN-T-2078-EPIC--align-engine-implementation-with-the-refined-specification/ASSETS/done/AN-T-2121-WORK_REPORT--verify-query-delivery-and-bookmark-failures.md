---
atom_family: TKT
atom_id: AN-T-2121
container:
  atom: AN-T-2078
priority: 2
context:
  template: work_report
state:
  status: done
  version: 1
  updated_at: 2026-11-11 06:42:51 +0400
---

## Summary

Verify query delivery and Bookmark failures

## Details

Image d520960c81eb passed HTTP/MCP full exports, stable pages, CTE preview, Check metadata, and Bookmark success/failure. Read-only disposable export and Journal mounts produced partial results on both interfaces. Completed query IDs still returned the exact rows.

Browser handling of the partial save and the remaining Evaluation checklist are open. Evidence: `.anechoic_tmp/CA-P-2791/CA-P-2852/acceptance-d520/`.
