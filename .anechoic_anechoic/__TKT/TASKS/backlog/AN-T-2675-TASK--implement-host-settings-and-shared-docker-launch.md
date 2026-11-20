---
identity:
  atom_id: AN-T-2675
context:
  container:
    atom: AN-T-872
  tier: 3
  template: task
state:
  status: backlog
  version: 5
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Implement host settings and shared Docker launch

## Objective

Implement the shared host settings reader and Docker launch material with a configurable My_Repos mount outside any Project. Keep machine-local settings out of repository authority and preserve existing settings rather than overwriting them.

## Details

One Task per file; each leaf has at most 15 minutes own work and must be decomposed before extending it. Review and update dependent Tasks after observed predecessor outcomes. Use the selected Project virtual environment, configured Project Temporary State and only broken/related checks. Do not replay uncertain effects, replace production or run the full suite.

### Definition of Done

Focused temporary-config and Compose/launch checks prove explicit validated roots, correct bind mount and endpoint parameters without touching production.
