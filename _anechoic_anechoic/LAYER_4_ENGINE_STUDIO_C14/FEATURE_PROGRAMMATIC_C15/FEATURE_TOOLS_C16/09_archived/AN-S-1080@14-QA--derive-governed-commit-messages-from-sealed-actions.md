---
atom_family: SPEC
atom_id: AN-S-1080
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 14
  updated_at: 2026-09-12 04:12:43 +0400
---
## Summary

Derive Governed Commit Messages from Sealed Actions

# Derive Governed Commit Messages from Sealed Actions

## Claim checked

the canonical Git commit message is a deterministic Projection of **=1** sealed Git-effect action: an Initiative-based real-change action **or** a distinct Journal-only batch action.

## Test case

prepare one sealed real-change action whose Initiative comes from human input **and** one sealed Journal-only batch action. independently render `<initiative-summary> | <CHANGE_CLASS> | <affected-subject>` **and** `JOURNAL BATCH | APPEND | <journal-batch-id>`, **then** compare both renderings with the corresponding Git commit subjects.

## Acceptance criteria

**every** Git commit subject is byte-identical **to** its independently rendered Projection, **contains** no added prefix, suffix, quoting, normalization, line wrapping, **or** technical-parent substitution, **and** neither action accepts the other message class.

## Failure disposition

reject the flow at the first rendering mismatch, technical-parent substitution, **or** cross-class impersonation **and** report the sealed action **and** divergent output.
