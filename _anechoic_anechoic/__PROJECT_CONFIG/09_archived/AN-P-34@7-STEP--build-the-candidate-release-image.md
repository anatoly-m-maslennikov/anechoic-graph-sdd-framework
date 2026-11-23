---
atom_family: PROJECT_CONFIG
atom_id: AN-P-34
structure:
  container:
    component: C00
context:
  template: step
state:
  status: archived
  version: 7
  updated_at: 2026-10-24 11:29:41 +0400
---
## Summary

Build the candidate release image

# Summary

Build the candidate release image

## Step

This Step invokes CA-O-168 once with phase `candidate_image_build`, binding CA-O-175's staged package, exact source/context rows and immutable candidate image identity. The frozen Docker worker has no Docker socket and cannot substitute for host Candidate E2E.

## Details

It creates no authority from a tag, cached image or successful build alone. A build mismatch, host mount, stale package/source, unsafe context, failed result or missing Journal receipt stops without proof, promotion or old-image removal.
