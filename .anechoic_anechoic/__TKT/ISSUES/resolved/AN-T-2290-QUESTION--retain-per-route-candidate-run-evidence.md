---
atom_family: TKT
atom_id: AN-T-2290
structure:
  container:
    component: C00
  priority: 2
context:
  template: question
state:
  status: "resolved"
  version: 2
  updated_at: "2026-11-20T20:34:46.079377+00:00"
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
