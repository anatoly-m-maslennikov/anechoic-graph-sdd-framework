---
atom_family: TKT
atom_id: AN-T-260
structure:
  container:
    component: C00
  priority: 2
context:
  template: task
state:
  status: done
  version: 13
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Pass the full test suite before local release

## Objective

Pass the intended Local release tool tests before live copy and installation.

## Details

- Follow CA-P-1848's current direct happy path. Earlier snapshot, admission, selector, recovery and complete-corpus gate requirements are superseded.
- Commit everything before every release step and at the end, respecting Git ignore rules and secret exclusions.
- Stop and report a failed step for manual handling; no automatic rollback or retry.
- Preserve configuration, Project records and other Projects. Ignore .DS_Store.

- Completion evidence: All 16 intended Local, Public and MCP contract tests passed before the live Local release's copy and installation steps.
- Live Local receipt: .anechoic_runtime/simple_local_release/reports/epic1848-direct-local-20261012-001.md. Consolidated verification: .anechoic_tmp/epic1848/direct-local-completion.md.

## Definition of Done

The Objective is implemented and verified with actual evidence appropriate to this task. Record remaining manual issues. Mock tests do not prove live release, installation, MCP or PR completion.
