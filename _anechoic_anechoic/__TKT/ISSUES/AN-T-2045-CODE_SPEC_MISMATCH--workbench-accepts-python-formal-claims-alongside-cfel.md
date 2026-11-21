---
atom_family: TKT
atom_id: AN-T-2045
structure:
  container:
    component: C14
  priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: active
  version: 1
  updated_at: '2026-11-12T12:49:24.671712+00:00'
---
## Summary

Workbench accepts Python Formal Claims alongside CFEL

## Claim

### Prose Claim

In the ANECHOIC working tree based on `c0b983cb27`, `LAYER_2_FRAMEWORK_ENGINE/FEATURE_PROGRAMMATIC/FEATURE_APPS/APP_WORKBENCH/FEATURE_WORKBENCH_BACKEND/declaration_cfel.py` reads supported Python-labelled Formal Claim fences in addition to CFEL. CA-M-500@11 and CA-M-509@6 specify CFEL-only declaration facts for the current Workbench assets. The source currently permits both readers. Python migration is tracked separately in CA-P-3022. This observation concerns the checkout, with no claim that the mixed-language reader has been deployed.
