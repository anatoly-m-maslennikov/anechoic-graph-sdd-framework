---
atom_family: TKT
atom_id: AN-T-2225
container:
  component: C45
priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: resolved
  version: 1
  updated_at: '2026-11-21T00:55:51.786482+00:00'
---
## Summary

Workbench does not publish spec trace tables

## Concern

CA-M-1015@1 requires Workbench to publish Implementation objects and RMEDO pins through its query interface and keep them current as files change. The checkout defines a draft store in `FEATURE_IWE_CONSOLE_BACKEND/spec_trace.py`. The startup and watcher in `service_indexing.py` do not call it, and `query_schema.py` omits both trace tables.