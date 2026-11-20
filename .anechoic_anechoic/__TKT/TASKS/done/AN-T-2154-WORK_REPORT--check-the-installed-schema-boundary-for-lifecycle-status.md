---
identity:
  atom_id: AN-T-2154
context:
  container:
    atom: AN-T-2078
  tier: 4
  template: work_report
state:
  status: canceled
  version: 1
  updated_at: 2026-11-11 09:24:07 +0400
---

## Summary

Check the installed schema boundary for lifecycle Status

## Details

Tested the Workbench Header compiler with the native base and Code Synopsis declarations. It delivers a Status column format, but no allowed values or qualified Status domain. The separate graph projection extractor rejects the qualified literal and does not feed the lifecycle adapters. Installed query_run shows the two expected Status columns. Evidence is in `.anechoic_tmp/CA-P-2791/CA-P-2934/status-formal-candidates/workbench-header-compiler-status.json`. CA-C-730 still tracks the required lifecycle Status input.
