---
identity:
  atom_id: AN-T-2069
context:
  container:
    component: C14
  tier: 4
  template: Code-Spec Mismatch
state:
  status: active
  version: 1
  updated_at: '2026-11-12T12:59:09.995903+00:00'
---
## Summary

Local Release packages less than the specified Engine tree

## Claim

### Prose Claim

CA-D-562@25 names the complete Engine tree as the runtime package source. `LAYER_5_FRAMEWORK_DELIVERY/RELEASE_VERSION/release_support.py` packages the Programmatic subtree and the canonical Skill, excluding selected source and test carriers. The package can omit Engine files named by the Delivery scope. The reviewed checkout separately defers several Engine areas, so the correct package boundary needs a spec decision.
