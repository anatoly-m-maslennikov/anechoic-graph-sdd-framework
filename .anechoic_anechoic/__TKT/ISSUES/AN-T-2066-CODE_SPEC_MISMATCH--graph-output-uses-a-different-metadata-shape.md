---
identity:
  atom_id: AN-T-2066
context:
  container:
    component: C14
  tier: 4
  template: Code-Spec Mismatch
state:
  status: active
  version: 1
  updated_at: '2026-11-12T12:59:01.708450+00:00'
---
## Summary

Graph output uses a different metadata shape

## Claim

### Prose Claim

CA-D-634@23 requires a Markdown Graph Projection with `type: Entities Graph`, `named_selection`, `source_of_truth` and `sources`. `FEATURE_TOOLS/GENERATE_ENTITY_GRAPH/readable_entity_tree.py` emits a Map or Catalog with a nested `source` mapping. CA-D-653@16 calls for persistent focused Subject Graph carriers. The inspected `render_subject_projections.py` path writes the focused body to stdout. No caller-side publishing was tested.
