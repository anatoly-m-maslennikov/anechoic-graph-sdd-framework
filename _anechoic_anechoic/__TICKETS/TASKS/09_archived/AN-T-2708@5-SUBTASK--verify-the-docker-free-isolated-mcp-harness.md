---
atom_family: TKT
atom_id: AN-T-2708
container:
  component: C15
priority: 2
context:
  template: task
  label: Subtask
state:
  status: archived
  version: 5
  updated_at: 2026-10-24 13:39:34 +0400
---
## Summary

Verify the Docker-free isolated MCP harness

# Summary

Verify the Docker-free isolated MCP harness

## Objective

Run the focused interactive-continuation checks in a naked isolated harness
without Docker or the production MCP port. Verify that current-session prompt
return, validated submission, pending/terminal transitions, explicit Project
binding and no-replay behavior remain attributable under the source-first O016
configuration.

## Details

Own work is bounded to 15 minutes. Use disposable frozen Project inputs, a
distinct nonproduction state/port if an HTTP boundary is required, locked uv,
and Project Temporary State. Do not start containers, touch production, replay
uncertain history, rebuild projections as authority, run the full suite, or
publish Git changes. Keep implementation, harness and real-Manifest journey
evidence separate; a Docker-free pass cannot claim runtime admission.

### Definition of Done

The focused naked-harness command passes or returns explicit bounded failures
for prompt/result and source-binding cases, with receipt paths, protected
production equality and the remaining complete real-Manifest gate recorded.

### Accepted completion evidence

The final Docker-free naked stdio smoke passed with 23 valid tools and an exact-path preview, using `.anechoic_tmp/naked-mcp-final-20261022-1829`. It confirms the focused prompt/result and source-binding harness without Docker or the production port; it does not claim Docker runtime admission, current installed Project binding or deployment.

