---
atom_family: PROJECT_CONFIG
atom_id: AN-P-38
structure:
  container:
    component: C00
context:
  template: step
state:
  status: archived
  version: 7
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Run the closed candidate Unit gate

# Summary

Run the closed candidate Unit gate

## Step

This Step invokes CA-O-168 once with phase `closed_unit_gate`, binding CA-O-175's exact private compiled candidate, frozen active-source boundary, and declared Unit/source partition.

## Details

Every declared Unit/source testcase must terminal-pass for the frozen candidate; skipped, excluded, missing, focused, cached, or historical results are non-pass. Host-capable Candidate E2E remains CA-O-182, and CA-O-184 alone aggregates the complete Release Gate. This Step does not clear, copy, compile, install, publish, or retry.
