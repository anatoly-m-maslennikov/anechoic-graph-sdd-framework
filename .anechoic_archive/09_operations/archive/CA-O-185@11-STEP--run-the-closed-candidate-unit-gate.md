---
atom_id: CA-O-185@11
ref_id: CA-O-185@11
container:
  scope_unit: CA-SU-00
role: Operations
form: Step
topics:
  main_subject: 'Subject/anechoic/Step//Release Version/Step: run closed candidate
    Unit gate'
  dependencies:
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Operations/Type:
    Workflow'
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Operations/Type:
    Step'
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Operations/Type:
    Action'
  - Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Quality/Verification
  - Subject/ANECHOIC/Graph/Node/Project Model/Selection//Methodology Sources
  - Subject/ANECHOIC/Graph/Node/Project Model/History/Journal
tier: 3
relations:
  part_of:
  - CA-O-164
  invokes:
  - CA-O-168
status: Archived
version: 11
updated_at: 2026-10-27 19:59:47 +0400
carrier_destination:
  file:
    name: CA-O-185@11-STEP--run-the-closed-candidate-unit-gate.md
    path: .anechoic_anechoic/09_operations/archive
current_scope_unit: anechoic
author: Anatoly Maslennikov
---
# Summary

Run the closed candidate Unit gate

## Step

This Step invokes CA-O-168 once with phase `closed_unit_gate`, binding CA-O-175's exact private compiled candidate, frozen active-source boundary, and declared Unit/source partition.

## Details

Every declared Unit/source testcase must terminal-pass for the frozen candidate; skipped, excluded, missing, focused, cached, or historical results are non-pass. Host-capable Candidate E2E remains CA-O-182, and CA-O-184 alone aggregates the complete Release Gate. This Step does not clear, copy, compile, install, publish, or retry.
