---
atom_family: TKT
atom_id: AN-T-2047
container:
  component: C14
priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: resolved
  version: 1
  updated_at: '2026-11-21T00:54:41.350002+00:00'
---
## Summary

Ordinary Workbench refresh copies the full inventory

## Claim

### Prose Claim

CA-M-465@29 limits ordinary refresh work to changed sources and affected relations. CA-M-549@2 moves audits out of the lifecycle response path. `FEATURE_IWE_CONSOLE_BACKEND/source_reader.py` still copies and sorts the inventory on ordinary deltas. `FEATURE_IWE_CONSOLE_BACKEND/service.py` creates an `AuditSnapshot` from the full inventory under its refresh lock. Database writes and relation updates are targeted, and audit evaluation runs in its worker. Full snapshot preparation remains on the synchronous path. The review did not measure its share of elapsed time.
