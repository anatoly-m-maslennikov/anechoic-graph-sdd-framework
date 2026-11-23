---
atom_family: SPEC
atom_id: AN-S-1354
container:
  component: C43
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 1
  updated_at: 2026-11-05 02:30:51 +0400
---

## Summary

Test Workbench through its public interfaces

## Claim

Prefer end-to-end tests through the real browser, MCP and HTTP interfaces. Assert user-visible results, not private classes, constructor arguments, call counts or internal call order. Remove unit tests that only repeat those end-to-end checks. Keep focused tests for behavior that the end-to-end tests do not cover.

Use Playwright with Chromium for browser checks against the existing Workbench test container. Reuse that container; do not start a Vite development server or mock the Workbench backend. Keep browser testing dependencies in the frontend's development dependencies. Do not add retries.
