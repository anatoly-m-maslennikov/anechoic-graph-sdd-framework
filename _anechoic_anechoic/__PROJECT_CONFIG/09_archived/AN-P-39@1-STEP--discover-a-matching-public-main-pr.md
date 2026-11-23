---
atom_family: PROJECT_CONFIG
atom_id: AN-P-39
structure:
  container:
    component: C00
context:
  template: step
state:
  status: archived
  version: 1
  updated_at: 2026-10-10 19:05:19 +0400
---
## Summary

Discover a matching public `main` PR

# Summary

Discover a matching public `main` PR

## Step

This Step invokes CA-O-190 once before public-source freeze and records zero or one actual open Pull Request from `amm/dev` to `main` on the selected personal remote.

## Details

More than one match, a nonmatching base/head, an unsafe URL, or unavailable observation stops the Workflow. Discovery is read-only and does not infer a future URL.
