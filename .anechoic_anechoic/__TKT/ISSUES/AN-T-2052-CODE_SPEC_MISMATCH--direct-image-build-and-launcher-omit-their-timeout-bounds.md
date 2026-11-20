---
atom_family: TKT
atom_id: AN-T-2052
structure:
  container:
    component: C14
  priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: active
  version: 1
  updated_at: '2026-11-12T12:53:36.316167+00:00'
---
## Summary

Direct image build and launcher omit their timeout bounds

## Claim

### Prose Claim

CA-M-409@14 requires bounded external execution. The direct build CLI accepts `--build-timeout` but does not pass it to its build call. `FEATURE_MCP/docker/start_mcp.py` also launches its outer `uv run` subprocess without a deadline, even though inner operations have bounds.
