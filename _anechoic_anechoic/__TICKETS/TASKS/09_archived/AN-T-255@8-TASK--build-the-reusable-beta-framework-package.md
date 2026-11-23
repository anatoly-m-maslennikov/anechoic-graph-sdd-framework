---
atom_family: TKT
atom_id: AN-T-255
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 8
  updated_at: 2026-10-24 08:10:13 +0400
---
## Summary

Build the reusable beta Framework package

# Summary

Build the reusable beta Framework package

## Objective

Build the reusable installation folder from Engine code, Methodology, locked dependencies and the ca Skill.

## Details

- Follow CA-P-1848's current direct happy path. Earlier snapshot, admission, selector, recovery and complete-corpus gate requirements are superseded.
- Commit everything before every release step and at the end, respecting Git ignore rules and secret exclusions.
- Stop and report a failed step for manual handling; no automatic rollback or retry.
- Preserve configuration, Project records and other Projects. Ignore .DS_Store.

- Completion evidence: The reusable package contains Engine code, delivered Methodology, pyproject.toml, uv.lock, version.toml and the ca Skill; 3,065 delivered files match the installed runtime package.
- Live Local receipt: .anechoic_runtime/simple_local_release/reports/epic1848-direct-local-20261012-001.md. Consolidated verification: .anechoic_tmp/epic1848/direct-local-completion.md.

## Definition of Done

The Objective is implemented and verified with actual evidence appropriate to this task. Record remaining manual issues. Mock tests do not prove live release, installation, MCP or PR completion.
