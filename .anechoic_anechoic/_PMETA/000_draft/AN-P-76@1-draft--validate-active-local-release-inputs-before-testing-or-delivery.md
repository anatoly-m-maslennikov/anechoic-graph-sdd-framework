---
atom_family: PMETA
atom_id: AN-P-76
structure:
  container:
    component: C00
context: {}
state:
  status: draft
  version: 1
  updated_at: 2026-10-29 20:32:25 +0400
---
## Summary

Validate active local release inputs before testing or delivery

## Step

This Step invokes CA-O-165 once with phase `validate` to check current active Core Meta-Model, installed extension, Project Configuration sources, and delivery paths.

## Details

Missing, inactive, ambiguous, or mismatched inputs stop before tests or delivery effects and are reported for manual handling. This Step does not copy, compile, install, publish, or retry.
