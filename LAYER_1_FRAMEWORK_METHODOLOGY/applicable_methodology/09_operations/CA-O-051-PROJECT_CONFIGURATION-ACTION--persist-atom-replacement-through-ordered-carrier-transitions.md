---
atom_id: CA-O-051
ref_id: CA-O-051
container:
  scope_unit: CA-SU-13
role: Operations
form: Action
topics:
  main_subject: Subject/anechoic/Action//Persist Atom Replacement
  dependencies:
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Operations/Type:
    Action'
  - Subject/ANECHOIC/Graph/Node/Project Model/Atom
  - Subject/ANECHOIC/Graph/Node/Project Model/Atom.Header.State.Version Number
  - Subject/ANECHOIC/Carrier/File
  - Subject/ANECHOIC/Graph/Node/Project Model/History/Journal
  - Subject/ANECHOIC/Carrier/File.Filename
  - ANECHOIC_MODEL <+ Relation
tier: 3
status: Active
version: 21
updated_at: 2026-10-27 19:59:44 +0400
carrier_destination:
  file:
    name: CA-O-051-PROJECT_CONFIGURATION-ACTION--persist-atom-replacement-through-ordered-carrier-transitions.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/09_operations
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
author: Anatoly Maslennikov
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/09_operations/CA-O-051-PROJECT_CONFIGURATION-ACTION--persist-atom-replacement-through-ordered-carrier-transitions.md
  source_atom_id: CA-O-051
  source_atom_revision: 21
  source_sha256: 0e223ae48b2588639142d9c32dab5d9ff4d68663cc9b86ce7e79a9ef843ddd9e
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
# Summary

Persist Atom replacement through ordered Carrier transitions

## Operation

Persist an accepted Atom replacement by resolving every distinct `IS_REPLACEMENT_FOR` target, including targets with different IDs and many-to-one replacement. Before publishing the Draft as Current, archive each eligible Current target once and skip every target already Archived, including one archived by composed Update. Archival preserves each target's Version and Updated At. Then publish the Draft with the supplied allowed Current Status and remove its Draft carrier. A changed Summary or Content Role creates a new identity promoted at Version 1; otherwise retain the Draft Version without a further increment. Derive carrier filename and location from the model.

Record actual business observations in the Journal independently; recording failure does not block the lifecycle effect. Stop on an effect failure and report completed and incomplete effects without retry, rollback, recovery or repair.
