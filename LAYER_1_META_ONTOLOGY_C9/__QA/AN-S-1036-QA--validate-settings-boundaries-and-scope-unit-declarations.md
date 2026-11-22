---
atom_family: SPEC
atom_id: AN-S-1036
container:
  component: C9
tier: 6
context:
  lens: QA
state:
  status: active
  version: 4
  updated_at: '2026-11-20T11:29:16.584115+00:00'
---

## Summary

Validate settings boundaries and Scope Unit Declarations

## Claim

Project settings resolve within their selected Project without cross-Project fallback. The Project Manifest owns Project settings and Component Manifests own Component structure; neither a Projection nor an observed folder replaces those authorities. A declared Component remains visible when its Carrier or active Goal is missing, and an undeclared folder remains an observation. Projection edits do not change Manifests or source Atoms.

Each Framework Instance resolves its Methodology Sources and Applicable Methodology beneath its own Project's `000_ANECHOIC_framework/` directory. Rebuilding one Project does not read, replace or modify another Project's sources, settings or compiled results. Report a missing selected instance rather than falling back to another Project or a former shared root. Nesting the framework directory does not change source Atom identity or make a Projection an authoritative Atom.
