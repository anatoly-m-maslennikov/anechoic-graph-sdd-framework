---
cce_version: cce_1
cce_form: evaluation
subjects:
  governs: Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Verification/Dynamic Testing
  depends_on:
  - Subject/ANECHOIC/Graph/Node/Project Model/Implementation/Code/Tool//DERIVE_CCE_CANONICAL_SIGNATURES
  - Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Data Handling/Data Validation
version: 17
updated_at: 2026-10-27 19:59:34 +0400
relations:
  evaluation_for:
  - CA-M-256
llm_session_ids:
- codex:01a02650-eff7-7453-8c37-0699b36773c6
atom_id: CA-E-422
status: archived
content_role: Evaluation
author: Anatoly Maslennikov
current_scope_unit: TOOLS
type: Policy
tier: 3
container:
  scope_unit: TOOLS
ref_id: CA-E-422@17
destination:
  file:
    name: CA-E-422@17-POLICY--verify-restricted-cce-canonical-signature-derivation.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/CA-SU-15_FEATURE_PROGRAMMATIC/CA-SU-16_FEATURE_TOOLS/06_evaluation/099_archived
---
## Summary

Verify Restricted CCE Canonical Signature Derivation

# Verify Restricted CCE Canonical Signature Derivation

the Evaluation **must** reject the Tool result **if** it violates CA-E-405 **or** changes one selected Source Atom.
