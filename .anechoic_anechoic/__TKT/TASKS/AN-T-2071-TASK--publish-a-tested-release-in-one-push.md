---
identity:
  atom_id: AN-T-2071
context:
  container:
    atom: AN-T-2070
  tier: 3
  template: task
state:
  status: active
  version: 2
  updated_at: '2026-11-12T16:36:29.191335+00:00'
---
## Summary

Publish a tested release in one push

## Work

1. Update RMEDO for Public Release publication and release materials.
2. Review and fix RMEDO against the linked Code Synopses and the Epic decision record.
3. Implement the reviewed RMEDO and verify the single push, linked newest-first Version History, PR readiness, and pushed commit evidence. Use the existing Atom ID and Version comments to identify the modules that implement the affected RMEDO and refresh their pins.

## Implementation entry points

- `LAYER_5_FRAMEWORK_DELIVERY/PUBLIC_RELEASE/public_release.py`
- `LAYER_5_FRAMEWORK_DELIVERY/PUBLIC_RELEASE/public_release_git.py`
- `LAYER_5_FRAMEWORK_DELIVERY/PUBLIC_RELEASE/public_release_materials.py`
