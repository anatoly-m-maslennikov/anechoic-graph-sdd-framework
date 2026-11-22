---
atom_family: TKT
atom_id: AN-T-2974
concern:
- component(id=C21)
- component(id=C30)
container:
  component: C21
priority: 2
context:
  template: problem
state:
  status: "archived"
  version: 1
  updated_at: "2026-11-22T02:02:55.831429+00:00"
---

## Summary

Installed MCP reports source changed for an Active bound Contract

## Observed

The Operator reported that installed MCP returned `source_changed` after
the guarded filesystem input Contract was bound to its implementation.

The same MCP resolves `AN-S-3303@1` as Active. The checkout binding
`LAYER_3_ENGINE_STUDIO_C14/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/ADAPTERS_C30/ADAPTERS_C30__spec_bind.yaml`
lists `AN-S-3303@1`. The failing tool, request, and source pin have yet
to be confirmed.

## Resolution criteria

- Reproduce the rejection with the installed MCP and identify the exact
  source pin or comparison that fails.
- Verify that the operation works with matching current sources. Preserve
  rejection when a required source has changed and report which check failed.
- Cover the matching and changed-source cases through the MCP entry point.

## References

AN-S-3303@1, AN-T-2944.
