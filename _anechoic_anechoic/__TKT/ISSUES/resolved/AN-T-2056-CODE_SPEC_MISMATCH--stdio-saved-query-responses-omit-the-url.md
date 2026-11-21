---
atom_family: TKT
atom_id: AN-T-2056
structure:
  container:
    component: C14
  priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: "resolved"
  version: 1
  updated_at: "2026-11-21T00:55:25.490540+00:00"
---
## Summary

Stdio saved query responses omit the URL

## Claim

### Prose Claim

CA-D-673@18 requires a saved query ID and URL. CA-M-1008@1 provides equivalent Tool behavior through HTTP and stdio. `FEATURE_MCP/registry_workbench_provider.py` presents a URL only when an HTTP request is available. `FEATURE_MCP/workbench_links.py` derives its base from that request. The stdio path returns the ID without the required URL.
