---
atom_family: TKT
atom_id: AN-T-258
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 7
  updated_at: 2026-10-24 09:20:34 +0400
---
## Summary

Consolidate duplicate delivery copies safely

# Summary

Consolidate duplicate delivery copies safely

## Objective

Report obsolete delivery copies for manual handling without making cleanup a release prerequisite.

## Details

- Follow CA-P-1848's current direct happy path. Earlier snapshot, admission, selector, recovery and complete-corpus gate requirements are superseded.
- Commit everything before every release step and at the end, respecting Git ignore rules and secret exclusions.
- Stop and report a failed step for manual handling; no automatic rollback or retry.
- Preserve configuration, Project records and other Projects. Ignore .DS_Store.

- Completion evidence: The old installed layout retains only empty or .DS_Store-only legacy directories. They contain no delivered files and are reported for optional manual cleanup; .DS_Store is ignored.
- Live Local receipt: .anechoic_runtime/simple_local_release/reports/epic1848-direct-local-20261012-001.md. Consolidated verification: .anechoic_tmp/epic1848/direct-local-completion.md.

## Definition of Done

The Objective is implemented and verified with actual evidence appropriate to this task. Record remaining manual issues. Mock tests do not prove live release, installation, MCP or PR completion.
