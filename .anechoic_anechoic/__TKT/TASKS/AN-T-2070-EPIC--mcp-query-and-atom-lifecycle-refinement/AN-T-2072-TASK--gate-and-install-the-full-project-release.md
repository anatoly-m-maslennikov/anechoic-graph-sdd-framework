---
atom_family: TKT
atom_id: AN-T-2072
structure:
  container:
    atom: AN-T-2070
  priority: 2
context:
  template: task
state:
  status: active
  version: 1
  updated_at: '2026-11-12T16:36:33.559467+00:00'
---
## Summary

Gate and install the full Project release

## Work

1. Update RMEDO for Local Release test gates, package scope, staging, installation, and image retention.
2. Review and fix RMEDO against the linked Code Synopses and the Epic decision record.
3. Implement the reviewed RMEDO and verify full-suite gating, temporary staging, healthy replacement, package contents, and retention of one previous image. Use the existing Atom ID and Version comments to identify the modules that implement the affected RMEDO and refresh their pins.

## Implementation entry points

- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/project_mcp_bootstrap.py`
- `LAYER_5_FRAMEWORK_DELIVERY/RELEASE_VERSION/local_release.py`
- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/COMPILE_APPLICABLE_METHODOLOGY/compile_applicable_methodology.py`
