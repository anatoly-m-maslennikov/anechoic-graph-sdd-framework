---
atom_family: SPEC
atom_id: AN-S-1132
container:
  component: C16
tier: 2
context:
  lens: SWD
state:
  status: archived
  version: 20
  updated_at: 2026-10-27 06:04:45 +0400
---
## Summary

Derive structural CRMED drafts from the Inventory

# Derive structural CRMED drafts from the Inventory

consume the exact current Implementation Inventory Projection produced by `CA-M-101` **and** apply the structural-adoption heuristic **to** the selected adoption frontier: a folder containing folders proposes an Area draft, a folder containing files proposes a Feature draft, **and** a language-native module **or** source file fallback proposes a Module draft. preserve ambiguity explicitly **when** the observed structure does **not** support one unambiguous proposal.

produce **only** CRMED drafts **and** their draft relations for operator review; do **not** convert Inventory observations directly into authority. the structural CRMED draft set is the primary adoption result, while the consumed Inventory remains an independently useful Step 1 result.
