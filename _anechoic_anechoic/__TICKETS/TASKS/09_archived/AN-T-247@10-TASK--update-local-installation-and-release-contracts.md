---
atom_family: TKT
atom_id: AN-T-247
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 10
  updated_at: 2026-10-24 10:29:57 +0400
---
## Summary

Update local installation **and** release contracts

# Summary

Update local installation **and** release contracts

## Objective

Specify the direct Local copy, compile, installation and Git checkpoint steps.

## Details

- Follow CA-P-1848's current direct happy path. Earlier snapshot, admission, selector, recovery and complete-corpus gate requirements are superseded.
- Commit everything before every release step and at the end, respecting Git ignore rules and secret exclusions.
- Stop and report a failed step for manual handling; no automatic rollback or retry.
- Preserve configuration, Project records and other Projects. Ignore .DS_Store.

- Completion evidence: The direct Local operation contracts and existing run_local_release entrypoint specify the tested copy, compile, install and Git-all checkpoint sequence. The live Local Run completed.
- Live Local receipt: .anechoic_runtime/simple_local_release/reports/epic1848-direct-local-20261012-001.md. Consolidated verification: .anechoic_tmp/epic1848/direct-local-completion.md.

## Definition of Done

The Objective is implemented and verified with actual evidence appropriate to this task. Record remaining manual issues. Mock tests do not prove live release, installation, MCP or PR completion.
