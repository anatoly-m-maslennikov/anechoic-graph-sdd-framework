---
atom_family: PROJECT_CONFIG
atom_id: AN-P-28
structure:
  container:
    component: C27
context:
  template: action
state:
  status: active
  version: 19
  updated_at: '2026-11-21T21:51:27.960780+00:00'
---

# Summary

Verify candidate release package and image

## Action

Use C19 Test Suite to run unit checks before image preparation, then end-to-end and canary checks against the exact candidate image. Build the candidate directly with Docker. A failed or incomplete check stops before installation; report the observed result without Journal.
