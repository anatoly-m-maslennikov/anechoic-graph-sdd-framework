---
atom_family: TKT
atom_id: AN-T-2107
container:
  atom: AN-T-2078
priority: 2
context:
  template: work_report
state:
  status: done
  version: 1
  updated_at: 2026-11-11 03:06:23 +0400
---

## Summary

Verify shared Views and result grid

## Details

Nine real-image browser tests passed in 13.2 s: exact saved-View reuse, context/palette rename and query-only duplication, global sorting/filtering/grouping across cached result pages, independent filters, NULL versus literal null groups, dotted column names, light/dark contrast, source newlines and Unicode/full-value actions. Eight in-process HTTP/MCP Workspace E2E tests passed, including E819's declared Project name differing from the folder basename and absent from saved Workspace documents.

Refreshed the generated development MCP registry; its stale descriptors correctly blocked the first run. Updated row-asserting transport tests to request inline delivery explicitly. The API fixture uses a real polling observer because sandboxed macOS FSEvents could not start and crashed the initial host run; native Linux watcher acceptance is separately recorded in P2925. No production watcher fallback was added. Current Compact browser checks and the recovered historical proxy measurements remain available; the exact original screenshot build/zoom is unverified. P2815 stays Active until the complete adopted View/result-lifetime/display checklist is reconciled; this Report does not close the Epic.

Evidence: .anechoic_tmp/CA-P-2791/CA-P-2815/browser-view-grid.log, .anechoic_tmp/CA-P-2791/CA-P-2818/workspace-e2e-polling.log and .anechoic_tmp/p2791-implementation-20261111/frontend/compact-implementation-report.md.
