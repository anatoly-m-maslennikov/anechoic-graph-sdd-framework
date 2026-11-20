---
atom_family: PMETA
atom_id: AN-P-16
structure:
  container:
    component: C16
context:
  template: action
state:
  status: active
  version: 17
  updated_at: 2026-11-02 15:49:28 +0400
---
## Summary

Ingest one external Analysis

# Ingest one external Analysis

Ingest External Analysis **means** the reusable Action that produces one attributable external-Analysis envelope **without** adopting its Claims as Project authority under CA-R-1145. its modeled boundary is the complete requested result; partial comparison, incomplete attribution, **or** an unreported unresolved input is **not** an independently successful outcome.

## Applicable when

use this Action **when** one external review **or** Analysis **must** be represented within a bounded project-analysis frontier **without** becoming accepted project authority.

## Action

1. resolve the external Analysis source identity, source digest, transformation session, **and** exact target frontier.
2. preserve the imported content **in** a provenance envelope that identifies its source, target frontier, **and** **all** declared transformations.
3. mark **every** imported claim as non-authoritative **and** require a separate governed adoption decision **before** **any** accepted project authority is created **or** revised.
4. return the envelope **and** explicit provenance links **without** editing source carriers **or** target authority.
5. reject a missing source identity, source digest, target frontier, **or** transformation provenance rather than filling it with inference.

## Outcome

one external Analysis is represented **in** an attributable bounded provenance envelope while its claims remain distinct from accepted project authority.

## Failure or stop

do **not** ingest an Analysis with incomplete provenance **and** do **not** create, revise, **or** imply adoption of **any** project authority.
