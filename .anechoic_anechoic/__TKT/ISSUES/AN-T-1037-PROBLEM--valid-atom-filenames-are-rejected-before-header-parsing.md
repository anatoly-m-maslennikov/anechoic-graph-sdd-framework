---
atom_family: TKT
atom_id: AN-T-1037
structure:
  container:
    component: C45
  priority: 2
context:
  template: problem
state:
  status: active
  version: 1
  updated_at: 2026-11-10 04:02:58 +0400
---

## Summary

Valid Atom filenames are rejected before Header parsing

## Concern

The filename marker matcher greedily selects later words such as `runtime-draft` or a Plan ID mentioned in the slug as if they were the Atom Role. A valid Header then cannot qualify the source, because candidate selection requires the guessed filename Role to match first.

## Details

Current examples include C526, C527, C533 and C283. Source layouts should not be renamed merely to avoid ordinary slug words. P2859 owns the narrow reader correction; undeclared source directories remain a separate boundary.
