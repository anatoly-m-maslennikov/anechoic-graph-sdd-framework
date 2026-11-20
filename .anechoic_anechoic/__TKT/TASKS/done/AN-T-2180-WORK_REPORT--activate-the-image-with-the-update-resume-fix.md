---
identity:
  atom_id: AN-T-2180
context:
  container:
    atom: AN-T-2078
  tier: 4
  template: work_report
state:
  status: canceled
  version: 1
  updated_at: 2026-11-11 20:08:17 +0400
---

## Summary

Activate the image with the Update resume fix

## Details

The current-code image includes the Update resume fix and 16 verified native placement inputs. The exact-image canary passed public Archive and Change Status on a disposable Project. Live health, Workbench frontend and HTTP query, and MCP query_run passed after activation.

Both Workbench guards passed. Cold indexing took 25.2 seconds. The 500-Atom batches took 2.5–6.5 seconds. The resource guard peaked at 524 MiB with zero OOM kills. CA-C-730 tracks admission for the four authoring tools.
