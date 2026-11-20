---
identity:
  atom_id: AN-T-2677
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

Implement request-bound multi-Project MCP routing

## Objective

Add shared MCP routing from an explicit caller Project root to its canonical execution owner. Validate mounted-root containment and exact Project identity; preserve each native request and response and never select a Project globally.

## Details

One Task per file; each leaf has at most 15 minutes own work and must be decomposed before extending it. Review and update dependent Tasks after observed predecessor outcomes. Use the selected Project virtual environment, configured Project Temporary State and only broken/related checks. Do not replay uncertain effects, replace production or run the full suite.

### Definition of Done

Concurrent/interleaved two-Project calls retain correct settings, prefix, source frontier, state, output and errors; missing/outside/unsafe roots refuse without fallback.
