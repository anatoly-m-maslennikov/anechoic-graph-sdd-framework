---
atom_id: CA-O-103
ref_id: CA-O-103
container:
  scope_unit: CA-SU-13
role: Operations
form: Action
topics:
  main_subject: Subject/anechoic/Action//Atom Content Authoring
  dependencies:
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Operations/Type:
    Action'
  - Subject/ANECHOIC/Graph/Node/Project Model/Atom
  - Subject/ANECHOIC/Graph/Node/Project Model/Atom.Content
  - Subject/ANECHOIC/Graph/Node/Project Model/Atom.Details
  - Subject/ANECHOIC/Graph/Node/Project Model/Atom.Summary
  - Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role
  - ANECHOIC_MODEL <+ Carrier/File
  - ANECHOIC_MODEL <+ Atom.Content.Summary
tier: 3
status: Active
version: 16
updated_at: 2026-10-27 19:59:45 +0400
carrier_destination:
  file:
    name: CA-O-103-PROJECT_CONFIGURATION-ACTION--author-atom-content-before-summary.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/09_operations
current_scope_unit: PROJECT_CONFIGURATION
claim_target_scope_unit: PROJECT_CONFIGURATION
author: Anatoly Maslennikov
projection:
  source_carrier_path: ../../../.anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/09_operations/CA-O-103-PROJECT_CONFIGURATION-ACTION--author-atom-content-before-summary.md
  source_atom_id: CA-O-103
  source_atom_revision: 16
  source_sha256: b6c4cda90971b53a3244d65ee63438d303f33de7af46c4e6eccf185328c44e6a
  original_relations_sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
---
# Summary

Author Atom content before Summary

## Operation

Atom Content Authoring **means** the Action that takes an authorized authoring request, the Atom's Content Role, applicable authority, **and** **any** existing Revision, then prepares a coherent candidate through this flow:

1. for RMED, write Scope describing applicability, **then** write **=1** Claim within that Scope. for other Content Roles, write their primary contribution: Question, Concern, Objective, **or** Operation.
2. write the remaining body sections under CA-D-479 **and** the applicable Method. keep Details within the primary contribution **and** its applicability; RMED Details support the Claim **without** changing Claim **or** Scope.
3. review the primary contribution **and** its applicability against the completed remaining content. for RMED, review Scope **and** Claim together. **if** either needs changing, revise it explicitly within the authorized request **and** recheck the affected sections; never let Details silently change the contribution **or** applicability.
4. derive Summary from the finalized primary contribution within its applicability **only after** that review. for RMED, summarize the Claim within Scope, **not** Scope alone. for an existing Atom identity, compare the needed Summary with its established value; **if** a change is needed, return replacement required under CA-R-1464 rather than mutating that identity.
5. return the candidate, its review findings, **and** ready, replacement required, **or** blocked outcome. unresolved inconsistency **or** unmet permission **or** confidence gates returns blocked, **not** a ready candidate.

## Details

this Action prepares content; it does **not** persist, promote, replace, **or** archive an Atom. Carrier display order remains Summary first even though Summary is authored last. an Analysis TLDR is part of the other Markdown written **before** the primary-contribution review; it does **not** become the Atom Summary source.
