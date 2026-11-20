---
identity:
  atom_id: AN-T-2674
context:
  container:
    atom: AN-T-869
  tier: 3
  template: task
state:
  status: backlog
  version: 4
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Apply shared errors to Workflow executors

## Objective

Apply shared classification/diagnostics at actual Workflow execution owners, preserving observed partial/uncertain outcomes, cancellation and truthful business Journal transitions through the existing executor. Do not turn a failed business Workflow into a blocking runtime failure or fabricate a Run for preflight refusal.

## Details

One Task per file. Each leaf has at most 15 minutes own work; decompose before extending it. Review and update dependants after each predecessor's observed result. Use only broken/related checks, configured Project Temporary State and the selected virtual environment. No production mutation or full-suite run.

### Definition of Done

Focused executor checks cover request/artifact warnings, explicit runtime ERROR, truthful results/lifecycle and no replay/retry. Split if more than 15 minutes own work.
