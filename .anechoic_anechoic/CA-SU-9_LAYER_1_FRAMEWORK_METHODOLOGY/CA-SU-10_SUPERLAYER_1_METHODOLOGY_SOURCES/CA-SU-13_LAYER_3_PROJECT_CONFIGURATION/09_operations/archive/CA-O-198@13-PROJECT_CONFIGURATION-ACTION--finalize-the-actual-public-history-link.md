---
atom_id: CA-O-198@13
ref_id: CA-O-198@13
container:
  scope_unit: CA-SU-13
role: Operations
form: Action
topics:
  main_subject: Subject/anechoic/Action//Finalize actual public Version History link
  dependencies:
  - Subject/ANECHOIC/Graph/Node/Project Model/History
  - Subject/ANECHOIC/Carrier/Pull Request
  - Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Delivery/Git Commits
  - Subject/ANECHOIC/Graph/Node/Project Model/Execution
  - Subject/ANECHOIC/Graph/Node/Project Model/History/Journal
tier: 3
status: Archived
version: 13
updated_at: 2026-10-27 19:59:48 +0400
carrier_destination:
  file:
    name: CA-O-198@13-PROJECT_CONFIGURATION-ACTION--finalize-the-actual-public-history-link.md
    path: .anechoic_anechoic/CA-SU-9_LAYER_1_FRAMEWORK_METHODOLOGY/CA-SU-10_SUPERLAYER_1_METHODOLOGY_SOURCES/CA-SU-13_LAYER_3_PROJECT_CONFIGURATION/09_operations/archive
current_scope_unit: PROJECT_CONFIGURATION
author: Anatoly Maslennikov
---
# Summary

Finalize the actual public history link

## Action

Finalize the actual public history link **means** the mechanical action that either records a no-op for an already present actual PR link or appends a newly created PR’s exact URL to the concise Version History, follows up the commit and push, and refreshes the same PR.

## Details

The actual URL is required. The Action preserves its Tool-call input/result/effect/report references on its parent Action Run. It does not create another PR, guess a URL, merge, or replay an unknown remote outcome.
