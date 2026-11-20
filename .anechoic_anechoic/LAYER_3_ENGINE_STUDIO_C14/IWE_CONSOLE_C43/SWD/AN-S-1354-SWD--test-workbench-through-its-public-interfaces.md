---
identity:
  atom_id: AN-S-1354
context:
  container:
    component: C43
  tier: 4
  lens: SWD
state:
  status: active
  version: 4
  updated_at: 2026-11-10 20:47:54 +0400
---

## Summary

Test Workbench through its public interfaces

## Claim

### Prose Claim

Test Workbench through its real browser, MCP and HTTP interfaces.

Use Playwright with Chromium for browser checks against the existing Workbench test container. Reuse that container; do not start a Vite development server or mock the Workbench backend. Keep browser testing dependencies in the frontend's development dependencies. Do not add retries.
