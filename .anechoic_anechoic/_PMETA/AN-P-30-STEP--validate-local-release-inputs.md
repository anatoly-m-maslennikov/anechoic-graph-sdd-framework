---
identity:
  atom_id: AN-P-30
context:
  container:
    component: C27
  tier: 3
  template: step
state:
  status: active
  version: 11
  updated_at: 2026-11-09 15:54:30 +0400
---

# Summary

Validate local release inputs

## Step

This Step invokes CA-O-165 once with phase `validate` to check current active Core Meta-Model, installed extension, Project Configuration sources, and delivery paths.

## Details

Missing, inactive, ambiguous, or mismatched inputs stop before tests or delivery effects and are reported for manual handling. This Step does not copy, compile, install, publish, or retry.
