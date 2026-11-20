---
identity:
  atom_id: AN-T-2769
context:
  container:
    component: C9
  tier: 3
  template: question
state:
  status: resolved
  version: 1
  updated_at: '2026-11-18T22:11:00.425054+00:00'
---
## Summary

Choose the status directories for Anechoic carriers

## Concern

The new model defines four logical trees and versioned carrier filenames.
It needs a final physical destination for Draft, Current, and Archived
carriers within SPEC, PMETA, and TKT.

## Details

Use exact references and filename markers in the candidate model, and
validate logical tree membership. Keep the current placement principle as
the starting point for migration planning: shared Draft and Archived
directories and Current records local to their container. Confirm which
new roots own the shared directories and how Current folders are named.

Affected work is CA-P-3087 under CA-P-3074. Migration remains CA-P-3075.
