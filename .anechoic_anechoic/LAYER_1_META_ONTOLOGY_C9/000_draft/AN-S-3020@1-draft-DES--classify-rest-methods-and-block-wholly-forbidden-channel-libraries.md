---
identity:
  atom_id: AN-S-3020
context:
  container:
    component: C9
  tier: 3
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-11-18T22:05:29.691884+00:00'
---
## Summary

Classify REST methods and block wholly forbidden channel libraries

## Claim

### Prose Claim

For REST, `api` input covers `GET`, `HEAD`, and `OPTIONS`; `api` output covers `POST`, `PUT`, `PATCH`, and `DELETE`. Classify the operation once by method, regardless of the direction of its request and response bytes. When a channel is forbidden in both directions, reject imports of libraries for that channel; permitted adapters may handle I/O outside the direct allowance. Exact channel definitions and the enforcement mechanism remain unresolved in CA-A-1463 and are not chosen here.

## Details

Acceptance: REST GET, HEAD, and OPTIONS require input `api`, while POST, PUT, PATCH, and DELETE require output `api`; a library import for a channel denied by both directions is rejected, and an allowed adapter remains eligible. Reject assigning a REST method to the opposite direction or allowing a wholly forbidden channel's library import.

Sources: CA-A-1463@1-draft. Task: CA-P-3085.
