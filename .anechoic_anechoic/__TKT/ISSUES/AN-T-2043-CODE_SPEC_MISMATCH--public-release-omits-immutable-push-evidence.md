---
atom_family: TKT
atom_id: AN-T-2043
structure:
  container:
    component: C14
  priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: active
  version: 1
  updated_at: '2026-11-12T12:49:17.354439+00:00'
---
## Summary

Public release omits immutable push evidence

## Claim

### Prose Claim

In the ANECHOIC working tree based on `c0b983cb27`, `LAYER_5_FRAMEWORK_DELIVERY/PUBLIC_RELEASE/public_release.py` performs a Git push, then upserts the pull request and returns the Version and URL. The successful path records no immutable pushed commit and exact effect evidence in its result. `LAYER_5_FRAMEWORK_DELIVERY/release_events.py` records the Workflow result but does not record Step and Action Run evidence. CA-R-1925@15, CA-D-616@15 and CA-D-618@11 require these records. This comparison is source-only. No public push was run.
