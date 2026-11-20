---
identity:
  atom_id: AN-T-2375
context:
  container:
    component: C00
  template: problem
state:
  status: resolved
  version: 1
  updated_at: 2026-10-04 14:05:41 +0000
---
# Summary

Normalize the F13 Analysis TLDR heading

## Concern

The shared saved-carrier diagnostic rejected A1125's and A1138's literal TL;DR heading because current Analysis structure requires TLDR. The producer's earlier local checks accepted that variant; their carrier-conformance claims were therefore incomplete.

## Evidences

The root check returned the specific A1125 and later A1138 heading mismatches. Root changed only each heading token and Updated At; Summary, Version2, dispositions, evidence and history are unchanged. The correction is formatting, not semantic acceptance or runtime proof.

## Blast radius

Only this Analysis heading and the producer-versus-shared check discrepancy. Resolution requires the saved shared structural check to pass; no candidate comparison or Operation is changed.

The actual shared diagnostic passed at 2026-10-04 14:05:41 UTC over 228 Plans and 231 supporting carriers. This proves only its strict YAML, exact required headings/fields, unique IDs, Done placement and completion/BLOCKS DAG checks; it does not prove semantic or runtime correctness.
