---
atom_family: TKT
atom_id: AN-T-2051
container:
  component: C14
priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: resolved
  version: 1
  updated_at: '2026-11-21T00:55:08.096806+00:00'
---
## Summary

Launcher can pair an image with a later checkout fingerprint

## Claim

### Prose Claim

CA-R-1901@19 requires the selected image to match its compatibility identity. `FEATURE_MCP/docker/project_mcp_backend.py` obtains a selected image digest and recomputes the fingerprint separately. `project-mcp.compose.yaml` supplies that fingerprint as a container label. A checkout change between those reads can pair the prior digest with a newer label and satisfy the later container label comparison.
