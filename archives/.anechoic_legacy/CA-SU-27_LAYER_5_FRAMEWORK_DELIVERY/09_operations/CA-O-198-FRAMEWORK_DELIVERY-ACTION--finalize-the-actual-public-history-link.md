---
atom_id: CA-O-198
ref_id: CA-O-198
container:
  scope_unit: CA-SU-27
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
status: Active
version: 14
updated_at: 2026-11-09 15:54:30 +0400
carrier_destination:
  file:
    name: CA-O-198-FRAMEWORK_DELIVERY-ACTION--finalize-the-actual-public-history-link.md
    path: .anechoic_anechoic/CA-SU-27_LAYER_5_FRAMEWORK_DELIVERY/09_operations
current_scope_unit: FRAMEWORK_DELIVERY
author: Anatoly Maslennikov
relations: {}
---

# Summary

Finalize the actual public history link

## Action

Finalize the actual public history link **means** the mechanical action that either records a no-op for an already present actual PR link or appends a newly created PR’s exact URL to the concise Version History, follows up the commit and push, and refreshes the same PR.

## Details

The actual URL is required. The Action preserves its Tool-call input/result/effect/report references on its parent Action Run. It does not create another PR, guess a URL, merge, or replay an unknown remote outcome.
