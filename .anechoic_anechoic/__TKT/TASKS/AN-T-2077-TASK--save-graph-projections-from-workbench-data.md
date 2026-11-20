---
identity:
  atom_id: AN-T-2077
context:
  container:
    atom: AN-T-2070
  tier: 3
  template: task
state:
  status: active
  version: 1
  updated_at: '2026-11-12T16:36:41.098925+00:00'
---
## Summary

Save graph Projections from Workbench data

## Work

1. Update RMEDO for saved graph Projection delivery and Workbench source selection.
2. Review and fix RMEDO against the linked Code Synopses and the Epic decision record.
3. Implement the reviewed RMEDO and verify saved structural and focused Projections with declared metadata. Use the existing Atom ID and Version comments to identify the modules that implement the affected RMEDO and refresh their pins.

## Implementation entry points

- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/readable_entity_tree.py`
- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/current_entity_sources.py`
- `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/render_subject_projections.py`
