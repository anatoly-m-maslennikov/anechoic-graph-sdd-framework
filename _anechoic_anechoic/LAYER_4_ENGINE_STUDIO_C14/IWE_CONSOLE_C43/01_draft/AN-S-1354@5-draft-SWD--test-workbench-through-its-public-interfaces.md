---
atom_family: SPEC
atom_id: AN-S-1354
container:
  component: C43
tier: 4
context:
  lens: SWD
state:
  status: draft
  version: 5
  updated_at: '2026-11-13T20:47:54.455630+00:00'
---
## Summary

Test Workbench through its public interfaces

## Claim

### Prose Claim

Test Workbench through its real browser, MCP and HTTP interfaces.

For browser checks, use Playwright with Chromium against the existing Workbench test container. Reuse that container. Do not start a Vite development server or mock the Workbench backend. Keep browser testing dependencies in the frontend development dependencies. Do not add retries.
