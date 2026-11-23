---
atom_family: SPEC
atom_id: AN-S-1201
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 24
  updated_at: 2026-10-24 22:06:39 +0400
---
## Summary

Requirement — Keep provenance separate from evidence

# Summary

Requirement — Keep provenance separate from evidence

## Scope

provenance and Evidence for governed claims and Implementations.

## Claim

provenance establishes the origin, carrier identity, revision, sequence, **and** transformation history of a governed claim **or** Implementation. it does **not** by itself establish that the claim is correct, accepted, current, applicable, **or** sufficiently assured.

complete governed provenance remains owned under CA-R-1720. a storage-history record, Author identity, session identifier, signature, hash, **or** intact Carrier proves **only** the bounded historical fact it records. **none** of those facts becomes evidence for the carrier's semantic claim **without** a separate, explicit claim-bound Evidence relation.

Evidence used for reliance **must** identify the claim it supports, the relevant carrier **or** Journal Record, the producing **or** interpreting work **or** Method **when** material, **and** the applicable scope **and** time boundary. Verification remains a separate Evaluation conclusion. a claim, its carrier, **and** the work that created it **must not** silently evidence themselves.

## Details
