---
atom_family: PROJECT_CONFIG
atom_id: AN-P-30
structure:
  container:
    component: C00
context:
  template: step
state:
  status: archived
  version: 6
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Validate local release inputs

# Summary

Validate local release inputs

## Step

This Step invokes CA-O-165 once with phase `validate` to check current active Core Meta-Model, installed extension, Project Configuration sources, and delivery paths.

## Details

Missing, inactive, ambiguous, or mismatched inputs stop before tests or delivery effects and are reported for manual handling. This Step does not copy, compile, install, publish, or retry.
