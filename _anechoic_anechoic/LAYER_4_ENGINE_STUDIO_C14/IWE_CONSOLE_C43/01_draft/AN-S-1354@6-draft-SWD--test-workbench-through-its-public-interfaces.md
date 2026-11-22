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
  version: 6
  updated_at: '2026-11-14T08:20:37.793921+00:00'
---
## Summary

Test Workbench through its public interfaces

## Claim

### Prose Claim

Test Workbench through its real browser, MCP, and HTTP interfaces.
Run Playwright with Chromium against the existing Workbench test container.

## Details

- Keep browser dependencies in the frontend's development dependencies.
- Use the real backend. Skip Vite development servers and retries.
