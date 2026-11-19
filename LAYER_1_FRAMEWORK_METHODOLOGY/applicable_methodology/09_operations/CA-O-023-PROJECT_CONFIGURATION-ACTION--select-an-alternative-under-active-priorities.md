---
atom_id: CA-O-023
ref_id: CA-O-023
container:
  scope_unit: CA-SU-13
role: Operations
form: Action
topics:
  main_subject: Subject/anechoic/Action//Select Priority-Governed Alternative
  dependencies:
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Operations/Type:
    Action'
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Actor/Type: Operator'
  - Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Operation/Execution Control/Effect
    Authorization
  - Subject/ANECHOIC/Graph/Node/Project Model/Selection//PROJECT_PRIORITY_MODEL
  - Subject/ANECHOIC/Graph/Node/Project Model/Selection//PROJECT_LEXICOGRAPHIC
  - ANECHOIC_STRUCTURE <+ Entity/Object/Continuant/Selection//PROJECT_LEXICOGRAPHIC
tier: 3
relations:
  child_of:
  - CA-R-1487
status: Active
version: 20
updated_at: 2026-10-27 19:59:44 +0400
carrier_destination:
  file:
    name: CA-O-023-PROJECT_CONFIGURATION-ACTION--select-an-alternative-under-active-priorities.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/09_operations
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
author: Anatoly Maslennikov
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/09_operations/CA-O-023-PROJECT_CONFIGURATION-ACTION--select-an-alternative-under-active-priorities.md
  source_atom_id: CA-O-023
  source_atom_revision: 20
  source_sha256: a509d613d3a4ec2aab8954713f4d6d69d33cd81ca441afe77ef11f9552c0f6d3
  original_relations_sha256: 2cccfab5f9eb53e0f786c8f141ca6d892cd6285d32a2aceff4e7a46010d8ba97
---
# Summary

Select an alternative under active priorities

## Operation

Select Priority-Governed Alternative **means** the Action that applies resolved Operator priorities **to** candidate alternatives **and** returns a justified selection **or** an unresolved comparison.

### execution

1. obtain the effective priorities resolved under CA-O-022 for the affected context. unresolved priorities do **not** authorize selection.
2. reject **every** candidate that violates applicable authority **or** a non-negotiable constraint.
3. apply the selected model **to** the remaining alternatives using the available evidence. use CA-M-297 **only** for Operator-selected comparison by priority order; use the selected technique for another model.
4. return a selected alternative **only** **when** that model justifies the choice. retain the constraints, criterion evidence, **and** comparison result that justify it.

### unresolved comparison

**if** no admissible alternative remains **or** the model does **not** determine a selection:

- report the alternatives, constraints, evidence, **and** unresolved comparison **to** the Operator.
- identify incomplete criterion order, unresolved ties, **or** incomparable results **when** applicable.
- do **not** invent a tie-break, substitute an algorithm, **or** return an unsupported winner.

**if** the Operator changes the applicable priorities, use the newly resolved result under CA-O-022 **before** comparing again.

## Details
