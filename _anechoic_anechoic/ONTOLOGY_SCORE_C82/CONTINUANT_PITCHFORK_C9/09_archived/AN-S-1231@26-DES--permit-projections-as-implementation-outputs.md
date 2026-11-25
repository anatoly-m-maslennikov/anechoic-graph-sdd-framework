---
atom_family: SPEC
atom_id: AN-S-1231
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 26
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Permit Projections as Implementation outputs

## Claim

### Prose Claim


non-authoritative view Projections delivered as Implementation outputs.


a view Projection **may** be delivered as an Implementation output of its governing RMED **without** becoming an Atom **or** another source of truth for the facts it represents.

- its output contribution is I; its Artifact kind remains Projection **and** its content remains derived from its declared sources.

## Details

This permission concerns a derived view delivered as an Implementation output, not Implementation as a whole. Directly edited native Implementation realizes RMED and can be a source of truth for what actually exists; it is not a Projection. A generated dependency graph or another derived view of Implementation remains a Projection: update its sources, then rebuild the view through its Workflow.
