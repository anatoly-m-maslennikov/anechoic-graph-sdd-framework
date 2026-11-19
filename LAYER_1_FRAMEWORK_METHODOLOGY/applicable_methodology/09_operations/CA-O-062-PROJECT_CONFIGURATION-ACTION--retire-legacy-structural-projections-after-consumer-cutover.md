---
atom_id: CA-O-062
ref_id: CA-O-062
container:
  scope_unit: CA-SU-13
role: Operations
form: Action
topics:
  main_subject: Subject/ANECHOIC/Graph/Node/Project Model/Projection
  dependencies:
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Operations/Type:
    Action'
  - Subject/ANECHOIC/Graph/Node/Project Model/Projection
  - Scope Unit
  - Subject/ANECHOIC/Graph/Node/Project Model/Projection//PROJECT_SCOPE_UNIT_GRAPH
  - Subject/ANECHOIC/Carrier
  - ANECHOIC_STRUCTURE <+ Projection//PROJECT_SCOPE_UNIT_GRAPH
tier: 3
status: Active
version: 14
updated_at: 2026-11-02 19:44:26 +0400
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
author: Anatoly Maslennikov
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/09_operations/CA-O-062-PROJECT_CONFIGURATION-ACTION--retire-legacy-structural-projections-after-consumer-cutover.md
  source_atom_id: CA-O-062
  source_atom_revision: 14
  source_sha256: 6815bb27e68cad695480e238026ea046ab67286f1115d151ee7e2b8507bacc66
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
# Retire legacy structural Projections after consumer cutover

Retire Legacy Structural Projections **means** the Action that retires the obsolete Project Scope Unit Graph Sources Projection **or** Project Scope Unit Graph Projection **after** validated direct-consumer cutover.

- the selected target is a legacy Projection retained under CA-D-453 **or** CA-D-454, **not** authoritative Project Structure.
- retire that target **only** **after** its direct-consumer cutover is validated; an unresolved cutover does **not** satisfy this condition.
- preserve its recorded migration disposition **and** return the actual retirement result. this Action does **not** require rebuilding **or** refreshing the obsolete Projection **or** reintroducing consumer dependence.

this Action governs the retirement job **only**; it does **not** grant new mutation authority **or** prescribe the Tool implementation that performs it.
