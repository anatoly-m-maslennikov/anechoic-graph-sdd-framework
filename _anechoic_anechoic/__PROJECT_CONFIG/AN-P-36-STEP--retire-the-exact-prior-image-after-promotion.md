---
atom_family: PROJECT_CONFIG
atom_id: AN-P-36
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

Retire the exact prior image after promotion

## Step

After the exact candidate starts and passes readiness checks, remove only unused obsolete images with proven matching Project ownership. Preserve protected, foreign, unowned, uncertain and container-referenced resources. Report pending cleanup without force, global prune or uncertain retry.
