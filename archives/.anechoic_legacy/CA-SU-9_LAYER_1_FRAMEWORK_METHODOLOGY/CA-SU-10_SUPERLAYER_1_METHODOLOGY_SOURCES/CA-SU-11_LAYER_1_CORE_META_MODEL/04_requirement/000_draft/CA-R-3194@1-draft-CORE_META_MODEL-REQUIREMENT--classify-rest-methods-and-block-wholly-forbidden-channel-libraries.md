---
identity:
  atom_id: CA-R-3194
  ref_id: CA-R-3194@1-draft
context:
  container:
    scope_unit: CA-SU-11
  role: requirement
  form: requirement
  topics:
    main_subject: MODEL//ANECHOIC <+ Atom
  tier: 3
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:05:29.691884+00:00'
destination:
  file:
    name: CA-R-3194@1-draft-CORE_META_MODEL-REQUIREMENT--classify-rest-methods-and-block-wholly-forbidden-channel-libraries.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/04_requirement/000_draft
---
## Summary

Classify REST methods and block wholly forbidden channel libraries

## Claim

### Prose Claim

For REST, `api` input covers `GET`, `HEAD`, and `OPTIONS`; `api` output covers `POST`, `PUT`, `PATCH`, and `DELETE`. Classify the operation once by method, regardless of the direction of its request and response bytes. When a channel is forbidden in both directions, reject imports of libraries for that channel; permitted adapters may handle I/O outside the direct allowance. Exact channel definitions and the enforcement mechanism remain unresolved in CA-A-1463 and are not chosen here.

## Details

Acceptance: REST GET, HEAD, and OPTIONS require input `api`, while POST, PUT, PATCH, and DELETE require output `api`; a library import for a channel denied by both directions is rejected, and an allowed adapter remains eligible. Reject assigning a REST method to the opposite direction or allowing a wholly forbidden channel's library import.

Sources: CA-A-1463@1-draft. Task: CA-P-3085.
