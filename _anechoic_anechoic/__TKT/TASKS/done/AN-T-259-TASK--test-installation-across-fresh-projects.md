---
atom_family: TKT
atom_id: AN-T-259
structure:
  container:
    component: C00
  priority: 2
context:
  template: task
state:
  status: done
  version: 16
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Test installation across fresh Projects

## Objective

Test installation and configuration preservation in disposable Project fixtures.

## Details

- Follow CA-P-1848's current direct happy path. Earlier snapshot, admission, selector, recovery and complete-corpus gate requirements are superseded.
- Commit everything before every release step and at the end, respecting Git ignore rules and secret exclusions.
- Stop and report a failed step for manual handling; no automatic rollback or retry.
- Preserve configuration, Project records and other Projects. Ignore .DS_Store.

- Completion evidence: Six Local fixture tests passed, including active-only copy, configuration preservation, failure stop, actual temporary Git, and Local version numbering.
- Live Local receipt: .anechoic_runtime/simple_local_release/reports/epic1848-direct-local-20261012-001.md. Consolidated verification: .anechoic_tmp/epic1848/direct-local-completion.md.

## Definition of Done

The Objective is implemented and verified with actual evidence appropriate to this task. Record remaining manual issues. Mock tests do not prove live release, installation, MCP or PR completion.
