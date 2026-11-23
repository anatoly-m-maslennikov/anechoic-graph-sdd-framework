---
atom_family: TKT
atom_id: AN-T-264
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 8
  updated_at: 2026-10-24 08:16:43 +0400
---
## Summary

Pass the full test suite before public release

# Summary

Pass the full test suite before public release

## Objective

Pass the intended Public release tool tests before publication.

## Details

- Follow CA-P-1848's current direct happy path. Earlier snapshot, admission, selector, recovery and complete-corpus gate requirements are superseded.
- Commit everything before every release step and at the end, respecting Git ignore rules and secret exclusions.
- Stop and report a failed step for manual handling; no automatic rollback or retry.
- Preserve configuration, Project records and other Projects. Ignore .DS_Store.

- Completion evidence: The intended Local/Public/MCP release modules passed 16 tests (19.160 seconds). Actual Public Run epic1848-direct-public-20261012-001 then completed publication for version 0.4.3; this is not a mock-only completion claim.
- Public evidence: Run epic1848-direct-public-20261012-001 completed for 0.4.3; PR https://github.com/anatoly-m-maslennikov/anechoic-graph-driven-framework/pull/27. Journal started Event 803fbb4b-8b3a-4a2a-9839-a65251d46e02; completed Event 8bdb213a-13be-4f26-9c87-0a44dfc30b34.

- Public completion receipt: .anechoic_tmp/epic1848/direct-public-completion.md.

## Definition of Done

The Objective is implemented and verified with actual evidence appropriate to this task. Record remaining manual issues. Mock tests do not prove live release, installation, MCP or PR completion.
