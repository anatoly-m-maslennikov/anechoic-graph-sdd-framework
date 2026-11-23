---
atom_family: TKT
atom_id: AN-T-253
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 5
  updated_at: 2026-10-24 06:04:10 +0400
---
## Summary

Consolidate Methodology source **and** delivery paths

# Summary

Consolidate Methodology source **and** delivery paths

## Objective

Use the declared source, product and installed Methodology folders without compatibility migration.

## Details

- Follow CA-P-1848's current direct happy path. Earlier snapshot, admission, selector, recovery and complete-corpus gate requirements are superseded.
- Commit everything before every release step and at the end, respecting Git ignore rules and secret exclusions.
- Stop and report a failed step for manual handling; no automatic rollback or retry.
- Preserve configuration, Project records and other Projects. Ignore .DS_Store.

- Completion evidence: project_structure.toml declares the authoring sources below the Project methodology unit. Live source export, product compilation and installed copy used those paths without compatibility migration.
- Live Local receipt: .anechoic_runtime/simple_local_release/reports/epic1848-direct-local-20261012-001.md. Consolidated verification: .anechoic_tmp/epic1848/direct-local-completion.md.

## Definition of Done

The Objective is implemented and verified with actual evidence appropriate to this task. Record remaining manual issues. Mock tests do not prove live release, installation, MCP or PR completion.
