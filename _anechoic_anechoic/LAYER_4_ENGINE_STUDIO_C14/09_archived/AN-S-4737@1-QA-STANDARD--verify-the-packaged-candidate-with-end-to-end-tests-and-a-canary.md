---
atom_family: SPEC
atom_id: AN-S-4737
container:
  component: C14
tier: 1
context:
  template: STANDARD
  lens: QA
state:
  status: archived
  version: 1
  updated_at: '2026-11-23T17:59:16Z'
relations:
  IS_REFERENCE:
  - AN-S-3346
  - AN-S-4734
  - AN-S-4736
  - AN-S-4731
  - AN-S-3360
---

## Summary

Verify the packaged candidate with end-to-end tests and a canary

## Claim

### Prose Claim

#### End-to-End tests

Run the packaged checks against the exact immutable production candidate image
with the external development harness. The candidate contains no tests or
profiler. Apply AN-S-3360 to profiler restrictions. Exercise Workbench through
its real browser, MCP, and HTTP interfaces. Playwright uses the pinned
Chromium and the same packaged Workbench candidate in the existing Workbench
test container. Keep browser dependencies in frontend development
dependencies, outside the candidate image. Reuse that container. Do not start
a Vite development server, mock the Workbench backend, or add retries.

The image-test harness waits for observable readiness. The test Project is
isolated and access uses loopback. Affected workflows run only when the
verified selection is adopted. Until then, the configured required image
suite runs.

#### Canary

Run one Canary for every candidate after End-to-End checks pass and before
installation. Verify startup, MCP initialization, and a representative query.
Use a ping when a query is unavailable. Wait for observable readiness and
apply AN-S-4731 to liveness and abort behavior. A failed or incomplete
required check stops release.
