---
identity:
  atom_id: AN-T-2730
context:
  container:
    atom: AN-T-2737
  tier: 3
  template: task
state:
  status: done
  version: 7
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Refactor legacy stdio test harness before budget alignment

## Objective

Refactor the canonical legacy MCP stdio test harness into bounded, cohesive
fixture and helper responsibilities before changing its startup budget.

## Details

This is one bounded Task with at most 15 minutes of own work. The exclusive
source boundary is
102_FRAMEWORK_ENGINE/201_PROGRAMMATIC/204_MCP/tests/test_rmed_workflow_mcp.py
(the worker observed 305 source lines before extraction). Preserve its current functional assertions, discovery
and client behavior, and the production Gateway contract. Extract only the
cohesive seams needed for the later budget alignment; do not change timeout
values, production hot_reload.py, MCP bindings, runtime images or release
behavior in this Task.

## Definition of Done

Return the refactored canonical harness with small functions/modules, focused
behavioral parity checks, Ruff and strict Mypy results, and an explicit list
of any remaining startup-budget boundary. Do not run the full suite, live MCP,
release or deployment. CA-P-2634 may start only after this refactor is
verified.

## Execution checkpoint — 23 October 2026

The assigned worker performed the bounded refactor in the working tree: the
legacy harness was reduced from 305 to 200 lines and a new support helper was
added at 199 lines. The main test module now carries the RMED ownership header
for CA-M-395, CA-M-431 and CA-E-567. Twelve focused stdio/telemetry checks
passed in 117.937 seconds; Ruff, strict Mypy and the AST-diff check passed.
The independent reviewer found no behavioral or safety issue and returned
PASS after the header correction. This Task is Done for the refactor and its
focused verification. Production Gateway code, live binding, runtime image,
release and deployment remain unchanged; the separate bounded startup
alignment is CA-P-2634.
