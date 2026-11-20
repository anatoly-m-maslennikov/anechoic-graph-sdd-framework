---
atom_family: TKT
atom_id: AN-T-2756
structure:
  container:
    component: C9
  priority: 2
context:
  template: question
state:
  status: active
  version: 1
  updated_at: '2026-11-18T22:00:51.603985+00:00'
---
## Summary

Confirm direction for ordered sibling Component dependencies

## Concern

The Anechoic proposal requires forward dependencies between ordered sibling
Components. It leaves the direction of the dependency arrow implicit.

## Details

Use earlier-to-later in the candidate model, following CA-R-040@19-draft.
Verify both directions against one ordered sibling pair. Confirm whether
Anechoic keeps that rule before approval. Unordered siblings continue to
use their Contract and import rules.

Affected work is CA-P-3079 under CA-P-3074. Source proposal is CA-A-1463.
