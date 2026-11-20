---
identity:
  atom_id: AN-S-1354
context:
  container:
    component: C43
  tier: 4
  lens: SWD
state:
  status: draft
  version: 7
  updated_at: '2026-11-14T08:28:43.775259+00:00'
---
## Summary
Test Workbench through its public interfaces

## Claim
### Prose Claim
Test Workbench through its real browser, MCP and HTTP interfaces.
Use Playwright with Chromium against the existing Workbench test container.

## Details
### Browser checks
Use the container's real backend. Skip the Vite development server.
Keep browser test dependencies in the frontend's development dependencies. Run checks without retries.
