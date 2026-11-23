---
atom_family: TKT
atom_id: AN-T-1765
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 1
  updated_at: 2026-10-28 20:00:14 +0400
---
## Summary

Inventory Current sources and reconcile migration Drafts

# Summary

Inventory Current sources and reconcile migration Drafts

## Objective

Inventory Current sources and reconcile migration Drafts.

## Details

First stage; no new migration prerequisite.

Declare the source set from the governing Project Structure: Current Methodology RMED plus direct project-local RMED. Separate Core, installed Methodology sources and Project Configuration. Exclude Engine descendants and derived copies. Record actual counts and paths; do not reuse old graph counts as a fresh inventory. Classify existing next-version Drafts as usable, superseded, unrelated or unresolved. Reuse the correct successor rather than making a competing Draft.

Maintain the thin governs.tsv first, then depends_on.tsv. Columns stay Atom ID | old Subject | new Subject | status. Link the actual Draft from the Task's notes when needed; keep Claims and large evidence out of these tables. The initial Governs rows only record existing prepared Drafts, not a completed inventory. Register missing Definition Drafts separately until they have canonical IDs.

## Definition of Done

The selected source frontier and counts are explicit; every prepared Draft has a disposition; thin maps and missing-definition work are ready without promoting a source.

## Progress

Not started. Prior analysis and Drafts are inputs, not completion evidence.
