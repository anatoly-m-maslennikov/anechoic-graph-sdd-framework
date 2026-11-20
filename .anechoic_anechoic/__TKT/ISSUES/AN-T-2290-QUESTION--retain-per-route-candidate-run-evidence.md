---
identity:
  atom_id: AN-T-2290
context:
  container:
    component: C00
  template: question
state:
  status: active
  version: 2
  updated_at: 2026-10-23 03:14:50 +0400
---
# Summary

Retain per-route candidate Run evidence

## Concern

how should the final matrix retain exact per-route native Run and Journal evidence when the accepted harness cleans up disposable fixtures?

## Evidences

the current three-harness receipt retains aggregate/JUnit evidence but not native per-route IDs and result carriers. the harness checks those carriers before normal fixture cleanup.

## Blast radius

final traceability only; this does not alter the candidate, source model, execution or acceptance predicates.

## Decision

choose a bounded read-only capture of completed fixture evidence before cleanup under the existing Epic autonomy envelope. retain exact bytes, provenance and definition identities; collect no request/environment/source tree or secret. require independent collector review and actual captures before claiming this gap resolved.
