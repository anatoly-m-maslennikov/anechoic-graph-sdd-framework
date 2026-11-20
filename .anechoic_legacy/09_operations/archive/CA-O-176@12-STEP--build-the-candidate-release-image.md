---
atom_id: CA-O-176@12
ref_id: CA-O-176@12
container:
  scope_unit: CA-SU-00
role: Operations
form: Step
topics:
  main_subject: 'Subject/anechoic/Step//Release Version/Step: build candidate image'
  dependencies:
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Operations/Type:
    Workflow'
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Operations/Type:
    Step'
  - 'Subject/ANECHOIC/Graph/Node/Project Model/Atom/Content Role: Operations/Type:
    Action'
  - Subject/ANECHOIC/Carrier/Docker Image
  - Subject/ANECHOIC/Carrier
  - Subject/ANECHOIC/Graph/Node/Aspect/Engineering/Quality/Verification
  - Subject/ANECHOIC/Graph/Node/Project Model/History/Journal
tier: 3
relations:
  part_of:
  - CA-O-164
  invokes:
  - CA-O-168
status: Archived
version: 12
updated_at: 2026-10-27 19:59:47 +0400
carrier_destination:
  file:
    name: CA-O-176@12-STEP--build-the-candidate-release-image.md
    path: .anechoic_anechoic/09_operations/archive
current_scope_unit: anechoic
author: Anatoly Maslennikov
---
# Summary

Build the candidate release image

## Step

This Step invokes CA-O-168 once with phase `candidate_image_build`, binding CA-O-175's staged package, exact source/context rows and immutable candidate image identity. The frozen Docker worker has no Docker socket and cannot substitute for host Candidate E2E.

## Details

It creates no authority from a tag, cached image or successful build alone. A build mismatch, host mount, stale package/source, unsafe context, failed result or missing Journal receipt stops without proof, promotion or old-image removal.
