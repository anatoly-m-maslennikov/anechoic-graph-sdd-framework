---
atom_id: CA-M-368
ref_id: CA-M-368
container:
  scope_unit: CA-SU-27
role: Method
form: Decision
topics:
  main_subject: Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Delivery
  dependencies:
  - Subject/ANECHOIC/Carrier/Git Commit
  - Subject/ANECHOIC/Carrier/Git Repository
  - Subject/ANECHOIC/Carrier/Pull Request
  - Subject/ANECHOIC/Graph/Node/Project Model/Execution
tier: 4
relations:
  method_for:
  - CA-R-1925
  - CA-R-1926
  - CA-R-1927
status: Active
version: 14
updated_at: 2026-11-09 15:54:30 +0400
carrier_destination:
  file:
    name: CA-M-368-FRAMEWORK_DELIVERY-DECISION--bind-public-remote-effects-to-one-pr-identity.md
    path: .anechoic_anechoic/CA-SU-27_LAYER_5_FRAMEWORK_DELIVERY/05_method
current_scope_unit: FRAMEWORK_DELIVERY
claim_target_scope_unit: FRAMEWORK_DELIVERY
author: Anatoly Maslennikov
---

## Summary

Bind public remote effects to one PR identity

## Scope

the selected `amm/dev` push and `main` PR maintenance sequence.

## Claim

### Prose Claim

**the Operator** **must** use admitted native bindings to prove the immutable pushed commit and retain exactly one matching open PR identity through its create/update and any final refresh.

## Details

The bindings may use local subprocess facilities after their own admission; this Method adds no MCP prerequisite. It excludes merge and makes an identity change a stop condition.
