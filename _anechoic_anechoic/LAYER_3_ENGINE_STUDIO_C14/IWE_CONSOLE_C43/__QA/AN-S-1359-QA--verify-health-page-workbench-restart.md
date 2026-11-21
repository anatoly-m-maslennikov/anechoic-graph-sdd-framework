---
atom_family: SPEC
atom_id: AN-S-1359
structure:
  container:
    component: C43
  tier: 5
context:
  lens: QA
state:
  status: active
  version: 4
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Verify health-page Workbench restart

## Claim

### Prose Claim

Verify health Restart Workbench invokes the same native MCP action and shows actual ready/failure while page remains available on failure; GET HTML/JSON is read-only. Fixed Project form yields fresh queries, unknown old IDs and loadable saved items. Invalid Declaration reports failure without disabling MCP/page. Shared host requires explicit Project folder and restarts only it; missing/repeated/unknown fields reject before effect; blacklist remains enforced.
