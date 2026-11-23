---
atom_family: SPEC
atom_id: AN-S-466
container:
  component: C9
tier: 7
context:
  lens: DevOps
state:
  status: archived
  version: 29
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Serialize Project initialization identity

## Claim scope

the Operator-selected Project Name in the Project Settings TOML Carrier.

## Claim

the Project Settings TOML Carrier **must** encode the Operator-selected Project Name as its exact nonempty lowercase TOML string value **in** `project.name`, **before** the first Project Atom **or** Implementation is created.

## Details

validation **must** preserve the selected value exactly; it **must not** trim **or** convert its case. the complete supported field signature is governed by CA-D-366.

### Current source provenance

Current source: `.anechoic_anechoic/101_LAYER_1_FRAMEWORK_METHODOLOGY/METHODOLOGY_SOURCES/001_CORE_META_MODEL/07_delivery/CA-D-375-CORE_META_MODEL-ENG_DECISION--serialize-project-initialization-identity.md`, CA-D-375@27, SHA-256 `d86d451d292b2af19c799152c03940cf96f3693edad8f90fbca028d47f55303f`.
