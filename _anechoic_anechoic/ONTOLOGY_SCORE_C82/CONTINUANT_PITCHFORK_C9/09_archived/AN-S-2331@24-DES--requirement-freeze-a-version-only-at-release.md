---
atom_family: SPEC
atom_id: AN-S-2331
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 24
  updated_at: 2026-10-24 01:37:42 +0400
---
## Summary

Requirement — Freeze a version only at release

# Summary

Requirement — Freeze a version only at release

## Scope

target Versions and their selected authorized release events.

## Claim

a target Version **must** remain mutable **until** its selected authorized release event succeeds **and** the shared Journal records that outcome for the exact released candidate.

- the release record is a factual Journal Record under CA-R-1712, **not** an Operations Atom.
- its exact manifest binds the released governing Atom Revisions, Implementation **and** Delivery Revisions, applicable Evaluations **and** evidence, **and** release identifier.
- the selected release policy defines the event boundary. applicable Delivery authority defines the manifest **and** Journal representation; a selected Extension owns mechanism-specific references.
- planning allocation, implementation completion, readiness acceptance, **or** release-candidate naming does **not** freeze the Version **before** the successful event.

## Details

this Project Configuration Claim does **not** impose its release Workflow on **every** Project.
