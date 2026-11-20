---
identity:
  atom_id: AN-S-484
context:
  container:
    component: C9
  tier: 7
  lens: DevOps
state:
  status: archived
  version: 4
  updated_at: 2026-11-02 19:46:47 +0400
---
## Summary

Serialize Project Prefix

## Claim

### Prose Claim


the Operator-selected Project Prefix in the Project Settings TOML Carrier.


the Project Settings TOML Carrier **must** encode the Operator-selected Project Prefix as its exact nonempty uppercase TOML string value under CA-D-378 **in** `artifacts.identity.project_prefix` **before** the first Project Atom is created.

## Details

validation **must** preserve the selected prefix exactly; it **must not** trim **or** automatically uppercase it. The complete supported field signature is governed by the pending [Project Settings Content Decision](CA-D-366@28-draft-CORE_META_MODEL-ENG_DECISION--serialize-project-settings-content-in-toml.md). This Decision preserves the existing storage contract and first-Atom timing; uses of the Prefix are outside this logical-property correction.

### Current source provenance

Replacement candidate for the historical Current source: `.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-11_LAYER_1_CORE_META_MODEL/07_delivery/CA-D-376-CORE_META_MODEL-ENG_DECISION--serialize-the-project-atom-prefix.md`, CA-D-376@25, SHA-256 `3b04a0bd6dfce9eec731a550edcdd86c6fdba8560255477bd4810f3c254bd614`. This role-only Draft allocates no canonical Delivery identity and does not rename CA-D-376.
