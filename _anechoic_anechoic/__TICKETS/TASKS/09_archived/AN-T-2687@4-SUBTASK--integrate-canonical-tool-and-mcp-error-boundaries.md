---
atom_family: TKT
atom_id: AN-T-2687
container:
  component: C15
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 4
  updated_at: 2026-10-24 06:04:46 +0400
---
## Summary

Integrate canonical Tool and MCP error boundaries

# Summary

Integrate canonical Tool and MCP error boundaries

## Objective

Reuse the shared boundary at existing canonical public execution owners, including descriptor Tools and selected MCP routes where applicable. Preserve their different governed response schemas; reject invalid requests without disabling a healthy service. Apply once and keep registration/discovery effect-free.

## Details

One Task per file. After completion, review and update dependant Tasks before their execution. Actual business Workflow lifecycle recording remains with its declared executor; this Task does not invent it in an error decorator.

### Definition of Done

Focused public execution tests show WARNING plus request errors, runtime-only ERROR, no exception-message leakage, preserved sync/async results and no implicit Journal or retry. At most 15 minutes own work.

### Execution checkpoint

Integrated the shared boundary into registered Tool execution, selected MCP exception boundaries, workflow_orchestrator and the canonical Atom CLI. Existing public response schemas and provider-owned partial results are preserved. Missing logger/sink and missing implementation support remain observable; technical messages omit raw exception text/details. The MCP portfolio passed 53 cases in 22.254 seconds. The final related 32-case rerun passed and independent review approved. Missing shared implementation support remains WARNING unless its actual runtime owner explicitly classifies a blocking failure; no speculative runtime classification, retry or Journal emission was added. Source acceptance only; production is unchanged.
