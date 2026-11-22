---
atom_family: TKT
atom_id: AN-T-2226
container:
  component: C45
priority: 2
context:
  template: Code-Spec Mismatch
state:
  status: resolved
  version: 1
  updated_at: '2026-11-20T20:36:34.861998+00:00'
---
## Summary

A malformed spec trace can publish partial pins

## Concern

CA-M-1015@1 requires unreadable or unparseable trace files to be excluded. In `FEATURE_WORKBENCH_BACKEND/spec_trace.py`, `_pins` skips individual malformed entries and returns the remaining pins. A trace file with both a valid pin and a malformed pin therefore publishes an incomplete result.