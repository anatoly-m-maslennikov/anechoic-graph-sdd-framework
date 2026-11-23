---
atom_family: SPEC
atom_id: AN-S-1960
container:
  component: C21
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 1
  updated_at: 2026-11-11 00:16:05 +0400
---

## Summary

Verify universal tool specific help without execution

## Claim

### Prose Claim

For every admitted public MCP Tool, call with `help: true` and no normal business inputs, using the required trusted Project envelope where applicable. Assert that only that Tool's purpose and usage, parameter formats and allowed values, minimal examples, output contract and common errors are returned and that these agree with the same generated registry's schema and metadata. Verify that a newly registered provider receives help through the shared layer without a central Tool-name allowlist or duplicate handwritten help description.

Instrument business validation and provider dispatch, query/query-run, Workflow execution, source writes, business gates and business Journal Run creation: all remain untouched for help, including Tools whose normal calls require inputs or would mutate data. Technical diagnostics may be recorded. Verify invalid or mismatched binding rejects without cross-Project fallback, and that global blacklist and Project exclusions prevent direct help from exposing unavailable Tools. Verify normal calls still enforce their own business validation.

Send the minimal help-shaped request through each registered public MCP Tool boundary, with the required Project envelope and no business inputs; assert protocol schema acceptance and the specified response, rather than testing only the internal help handler.
