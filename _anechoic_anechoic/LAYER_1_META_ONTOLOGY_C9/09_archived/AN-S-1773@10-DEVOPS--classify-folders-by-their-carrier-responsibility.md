---
atom_family: SPEC
atom_id: AN-S-1773
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 10
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Classify folders by their Carrier responsibility

# Summary

Classify folders by their Carrier responsibility

## Scope

filesystem folders that carry or place Project artifacts.

## Claim

a filesystem folder **must** be classified as a Directory Carrier **only** **when** it carries a Structural Entity under CA-D-263.

- a folder's visibility **in** a graph **or** its containment of files does **not** itself establish that binding.
- administrative Content Role directories **and** Status subdirectories provide Carrier placement, **not** separate Structural Entities **or** Directory Carriers. Status placement remains governed by CA-D-295 **and** CA-D-352.

## Details
