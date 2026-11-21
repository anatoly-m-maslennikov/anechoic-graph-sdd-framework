---
atom_family: PROJECT_CONFIG
atom_id: AN-P-34
structure:
  container:
    component: C27
context:
  template: step
state:
  status: active
  version: 14
  updated_at: '2026-11-21T21:51:27.960780+00:00'
---

# Summary

Build the candidate release image

## Step

Build the candidate image directly with Docker after C19 unit checks pass. Bind subsequent checks to its immutable image identity. A failed or unsafe build stops release.
