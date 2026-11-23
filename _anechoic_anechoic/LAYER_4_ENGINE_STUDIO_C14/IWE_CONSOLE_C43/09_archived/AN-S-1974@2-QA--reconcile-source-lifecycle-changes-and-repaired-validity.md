---
atom_family: SPEC
atom_id: AN-S-1974
container:
  component: C43
tier: 5
context:
  lens: QA
state:
  status: archived
  version: 2
  updated_at: 2026-11-04 00:38:14 +0400
---
## Summary

Reconcile source lifecycle changes and repaired validity

## Claim scope

Atomic in-memory refresh of governed sources and Current declarations.

## Claim

### Prose Claim

The indexer atomically replaces in-memory `atoms` and `scope_units` state from selected governed sources and Current declarations. Current and Draft Atom carriers are included, including Done and Canceled Current statuses; Archived carriers are excluded. Only Current Scope Unit Declarations establish `scope_units` and schema authority. Each public and internal schema Projection row hash is SHA-256 of deterministic canonical row JSON excluding `hash`, with materialized relations in the Atom payload. Failures go to stderr, are skipped, and are not retried. No database file, temporary spill, or intermediate file exists.

## Details

| Fixture | Expected outcome |
| --- | --- |
| Current Active, Done, Canceled; Draft; and Archived carrier | The first four have Current/Draft `atoms` rows; Archived is absent. |
| Current and Draft Scope Unit Declarations | Only Current produces `scope_units` and schema authority. |
| Valid source edit adding direct relation | One atomic refresh replaces Atom row, materialized facts, and canonical row hash together. |
| Current declaration edit changing a mapped Property or derived Relation | The in-memory schema row and its `hash` refresh; affected model-guided parsing, materialized relations, public rows and their hashes refresh atomically. |
| Invalid, unreadable, or unstable source | Its rows are absent; stderr identifies it; unrelated valid rows remain; no retry is queued. |
| Move, deletion, or later repair | A later refresh reflects observed selected state without prescribing fingerprint algorithm or event workflow classification. |
| Filesystem observation during indexing | No database file, temporary spill, or intermediate file exists. |
