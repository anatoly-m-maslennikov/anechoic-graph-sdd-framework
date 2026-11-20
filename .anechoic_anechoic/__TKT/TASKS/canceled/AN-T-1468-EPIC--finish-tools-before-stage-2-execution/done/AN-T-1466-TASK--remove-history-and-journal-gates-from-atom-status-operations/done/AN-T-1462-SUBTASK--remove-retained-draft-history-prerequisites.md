---
atom_family: TKT
atom_id: AN-T-1462
structure:
  container:
    atom: AN-T-1466
  priority: 2
context:
  template: task
  label: Subtask
state:
  status: done
  version: 9
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Remove retained Draft-history prerequisites

## Objective

The ordinary affected execution path accepts manual Draft promotion without a retained-history directory or records. Existing retained records are optional evidence, not permission; actual failures and partial effects remain truthful.

## Details

### Accepted completion — 2026-10-16

The native path now accepts valid manual ID-free Drafts without retained-history/head/lineage/successor prerequisites. Every ordinary ID-free promotion uses a fresh unused ID; exact actual history and collision/source/permission safeguards remain. CA-P-2400 closed the independently found native publication race and descriptor-cleanup correction after independent review and exact post-cleanup Linux checks. CA-C-524 is Resolved; the unrelated host restriction remains Active in CA-C-523. Implementation commit `3d658ee7a` and CA-A-1215 record the bounded acceptance.

- [CA-P-2400 — Exclude concurrent native identity publication](02-CA-P-2387-TASK--remove-retained-draft-history-prerequisites/020_done/01-CA-P-2400-TASK--exclude-concurrent-native-identity-publication.md)

Remove trusted-head, never-identified/demotion lineage and consuming-successor prerequisites from the affected lifecycle and MCP/Workflow adapters. A valid manually authored Draft with no retained-history records must be promotable through the ordinary interface. Reuse existing identity/collision and source-write safety behavior; do not require retrospective registration, invent provenance or delete real history.

Estimated own work: at most 15 minutes; split further before execution if needed. After completion, review/update the next dependent task. A blocked leaf is postponed with a truthful Problem/Question Concern as appropriate; independent ready work continues.

## Definition of Done

The ordinary affected execution path accepts manual Draft promotion without a retained-history directory or records. Existing retained records are optional evidence, not permission; actual failures and partial effects remain truthful.
