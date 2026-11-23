---
atom_family: TKT
atom_id: AN-T-249
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 12
  updated_at: 2026-10-24 13:05:09 +0400
---
## Summary

Define the public-release Workflow **and** Tool contract

# Summary

Define the public-release Workflow **and** Tool contract

## Objective

Specify Public release, its one content prompt, version bump and GitHub publication.

## Details

- Follow CA-P-1848's current direct happy path. Earlier snapshot, admission, selector, recovery and complete-corpus gate requirements are superseded.
- Commit everything before every release step and at the end, respecting Git ignore rules and secret exclusions.
- Stop and report a failed step for manual handling; no automatic rollback or retry.
- Preserve configuration, Project records and other Projects. Ignore .DS_Store.

- Completion evidence: The Project-local Public operation and existing run_public_release entrypoint specify one content draft, Public version bump, Git-all checkpoints, amm/dev push and main PR publication without merge. Contract tests passed; this specification task does not claim live Public publication.
- Live Local receipt: .anechoic_runtime/simple_local_release/reports/epic1848-direct-local-20261012-001.md. Consolidated verification: .anechoic_tmp/epic1848/direct-local-completion.md.

## Definition of Done

The Objective is implemented and verified with actual evidence appropriate to this task. Record remaining manual issues. Mock tests do not prove live release, installation, MCP or PR completion.
