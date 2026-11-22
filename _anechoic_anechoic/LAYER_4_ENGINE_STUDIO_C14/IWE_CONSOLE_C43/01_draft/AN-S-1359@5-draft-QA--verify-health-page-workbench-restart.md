---
atom_family: SPEC
atom_id: AN-S-1359
container:
  component: C43
tier: 5
context:
  lens: QA
state:
  status: draft
  version: 5
  updated_at: '2026-11-13T20:47:43.495627+00:00'
---
## Summary

Verify health-page Workbench restart

## Claim

### Prose Claim

Verify that the health-page Restart Workbench action invokes the same native MCP action and displays the actual ready or failure result. The page remains available on failure. GET HTML and JSON are read-only.

For a fixed Project, verify that the form yields fresh queries, unknown old result IDs and loadable saved items. An invalid Declaration reports failure without disabling MCP or the page.

On a shared host, verify that the form requires an explicit Project folder and restarts only that Project. Missing, repeated or unknown fields are rejected before any effect, and the blacklist remains enforced.
