---
atom_family: TKT
atom_id: AN-T-1041
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

Export only active Methodology

## Objective

Copy active Methodology-source Atoms and compiler support files, excluding drafts and archives.

## Details

- Follow CA-P-1848's current direct happy path. Earlier snapshot, admission, selector, recovery and complete-corpus gate requirements are superseded.
- Commit everything before every release step and at the end, respecting Git ignore rules and secret exclusions.
- Stop and report a failed step for manual handling; no automatic rollback or retry.
- Preserve configuration, Project records and other Projects. Ignore .DS_Store.

- Completion evidence: Live comparison found no differences for 909 Core files, 1 Extension file and 111 Project Configuration files; only active Markdown Atoms and supporting files were delivered.
- Live Local receipt: .anechoic_runtime/simple_local_release/reports/epic1848-direct-local-20261012-001.md. Consolidated verification: .anechoic_tmp/epic1848/direct-local-completion.md.

## Definition of Done

The Objective is implemented and verified with actual evidence appropriate to this task. Record remaining manual issues. Mock tests do not prove live release, installation, MCP or PR completion.
