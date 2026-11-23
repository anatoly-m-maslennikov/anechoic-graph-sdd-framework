---
atom_family: TKT
atom_id: AN-T-257
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 11
  updated_at: 2026-10-24 13:05:09 +0400
---
## Summary

Run Tools **and** Docker MCP **from** the installed package

# Summary

Run Tools **and** Docker MCP **from** the installed package

## Objective

Start Docker MCP from the installed runtime and verify its actual endpoint.

## Details

- Follow CA-P-1848's current direct happy path. Earlier snapshot, admission, selector, recovery and complete-corpus gate requirements are superseded.
- Commit everything before every release step and at the end, respecting Git ignore rules and secret exclusions.
- Stop and report a failed step for manual handling; no automatic rollback or retry.
- Preserve configuration, Project records and other Projects. Ignore .DS_Store.

- Completion evidence: The installed-runtime launcher returned http://127.0.0.1:59995/mcp. Its container is healthy; actual MCP initialization succeeded and listed 33 tools.
- Live Local receipt: .anechoic_runtime/simple_local_release/reports/epic1848-direct-local-20261012-001.md. Consolidated verification: .anechoic_tmp/epic1848/direct-local-completion.md.

## Definition of Done

The Objective is implemented and verified with actual evidence appropriate to this task. Record remaining manual issues. Mock tests do not prove live release, installation, MCP or PR completion.
