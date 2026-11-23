---
identity:
  atom_id: CA-P-3068
  ref_id: CA-P-3068
context:
  role: plan
  form: Plan
  label: Task
  tier: 3
  container:
    atom: CA-P-3048
  topics:
    main_subject: ANECHOIC_STRUCTURE <+ Scope Unit//GENERATED_MODEL
relations:
  IS_BLOCKED_BY:
  - CA-P-3067
  - CA-P-3055
state:
  version: 1
  status: backlog
  updated_at: '2026-11-13T19:15:08.716253+00:00'
destination:
  file:
    name: CA-P-3068-TASK--regenerate-the-model-with-relation-applicability-and-property-ordering.md
    path: .anechoic_anechoic/CA-SU-14_LAYER_2_FRAMEWORK_ENGINE/03_plan/001_backlog
---
## Summary

Regenerate the Model with Relation applicability and Property ordering

## Work

After the Declaration migration and Engine and validator changes, rebuild the complete ANECHOIC Model from Current Declarations. Verify that the generated classes load and that the validator applies the endpoint levels and canonical Header order on actual Atoms. Check Form, Label, Topics when Label exists, and Form immediately followed by Topics when Label is absent.

Verify that Identity and Context each have Header as their immediate bearer and that Context immediately follows Identity.

## Specification

CA-R-2247, CA-R-2965, CA-R-2967, CA-R-3136, CA-E-828.

## Progress

Step 1 verified 36 native Relation Declarations and 14 inverse aliases against Current sources. CA-R-2762 owns BLOCKS. CA-R-1498@21 and CA-R-2732@4 explicitly name their source Relations.

Step 2 validated Entity Relation constraints against the registry and resolved inherited Properties through the declared Python classes. The live build generated 94 classes from 244 Current Declarations, and all 244 Declarations bound to MODEL_VALIDATION. A second build produced identical package bytes. The ordering check passed for Identity before Context and for Form, optional Label and Topics. Runtime write integration and Claim-language retirement remain open under CA-P-3055, CA-P-3060 and CA-P-3061.

The build resolved 244 Current Declarations and 50 Relation names. The second generation matched the checked-in Python package. Endpoint checks accepted INSTANCE_OF, HAS_INSTANCE and instance sibling ordering at their declared levels and rejected Model-to-Model use. Lifecycle prepared and validated real Header carriers CA-R-3070 and CA-P-3048, and rejected reversed Context ordering. The isolated image loaded the generated classes and Header rules under its normal runtime user.
