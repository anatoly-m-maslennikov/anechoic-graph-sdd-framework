---
atom_family: SPEC
atom_id: AN-S-1991
container:
  component: C15
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 21
  updated_at: 2026-11-09 14:19:14 +0400
---

## Summary

Use one Settings Reader across Engine software

## Claim

### Prose Claim

Verify that applicable Tool, App and MCP consumers use an immutable, validated settings snapshot with actual values, the selected Project, physical source path, raw SHA-256 digest and declared schema marker.

## Details

### Test case


Use a recording fake for the shared Reader and exercise representative applicable Tool, App and MCP consumers from each relevant PROGRAMMATIC child feature. A feature with no settings-dependent consumer adds no artificial test fixture.

### Acceptance criteria



Pass only when the Reader validates the complete input and returns the declared immutable snapshot with actual values, selected Project, source path, raw SHA-256 digest and schema marker. Each exercised consumer receives it explicitly, preserves its provenance, and performs no direct read, fallback, private default selection or mutation. Component-specific interpretation stays outside the Reader. The Reader does not query the Work Journal or infer logical currentness. A consumer may reuse an already validated snapshot; no per-consumer read count is imposed.

### Failure disposition

reject the bypassing consumer **until** it accepts the shared snapshot explicitly.

### Sources

- [Python documentation: `unittest.mock`](https://docs.python.org/3.14/library/unittest.mock.html)
- [CA-M-284 — Read Engine settings through one shared boundary](../05_method/CA-M-284-PROGRAMMATIC-DIRECT_POLICY--read-engine-settings-through-one-shared-boundary.md)
