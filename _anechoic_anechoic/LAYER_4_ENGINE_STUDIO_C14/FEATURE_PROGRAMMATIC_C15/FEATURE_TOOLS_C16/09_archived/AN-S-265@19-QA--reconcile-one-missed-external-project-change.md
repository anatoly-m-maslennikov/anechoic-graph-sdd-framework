---
atom_family: SPEC
atom_id: AN-S-265
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 19
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Reconcile one missed external project change

# Reconcile one missed external project change

## Claim checked

repository reconciliation recovers one Git-admitted project change that has no
Codex Hook event **without** inventing session provenance **or** duplicating work.

## Test case

create one admitted project change outside Codex Hook delivery, **then** run one
low-frequency reconciliation cycle twice against the resulting frontier.

## Acceptance criteria

pass **only** **when** the first cycle creates one governed action, identifies
repository reconciliation as its observation source, advances the normal commit
pipeline once, **and** the second cycle produces no duplicate action.

## Failure disposition

reject the reconciliation boundary **when** the change remains invisible, receives
invented Codex provenance, bypasses the normal pipeline, **or** is processed twice.

## Sources

- [Git documentation: porcelain v2](https://git-scm.com/docs/git-status#_porcelain_format_version_2)
- [CA-M-087 — Process one file change](../05_method/CA-M-087-TOOLS-ENG_DECISION--process-one-project-path-action.md)
