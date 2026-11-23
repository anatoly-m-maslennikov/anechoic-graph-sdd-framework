---
atom_family: PROJECT_CONFIG
atom_id: AN-P-31
structure:
  container:
    component: C9
context:
  template: step
state:
  status: archived
  version: 14
  updated_at: 2026-11-02 19:46:47 +0400
---
## Summary

Deliver active Methodology sources

# Summary

Deliver active Methodology sources

## Step

This Step invokes CA-O-166 once with phase `deliver_sources`, clearing replaceable product members and copying only the current active Core Meta-Model, installed extension, and Project Configuration sources into `LAYER_1_FRAMEWORK_METHODOLOGY/`.

## Details

It preserves protected product settings, does not broaden source membership, and does not compile, install, test, publish, or retry. A source or destination mismatch stops and is reported for manual handling.
