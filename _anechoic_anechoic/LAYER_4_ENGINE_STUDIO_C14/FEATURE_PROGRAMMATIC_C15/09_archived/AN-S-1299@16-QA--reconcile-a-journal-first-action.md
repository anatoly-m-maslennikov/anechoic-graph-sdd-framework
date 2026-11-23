---
atom_family: SPEC
atom_id: AN-S-1299
container:
  component: C15
tier: 1
context:
  lens: QA
state:
  status: archived
  version: 16
  updated_at: 2026-10-24 20:48:49 +0400
---
## Summary

Reconcile a Journal-first action

# Reconcile a Journal-first action

## Claim checked

one action whose canonical Journal record is prepared **before** its real-change
Git commit becomes reconciled **after** the exact reachable commit SHA is known.

## Test case

prepare one canonical Journal record for a sealed action, complete one
real-change commit, bind the record **to** that exact reachable commit, **and** commit
the Journal carrier later.

## Acceptance criteria

pass **only** **when** the action advances from `journal_recorded_git_pending` **to**
`reconciled` with **=1** record **and** one reachable real-change commit.

## Failure disposition

preserve the pending state **and** reject provenance reliance **until** binding is
complete.

## Sources

- [CA-M-192 — Reconcile independent Git and Journal provenance](../05_method/CA-M-192-PROGRAMMATIC-METHOD--reconcile-independent-git-and-journal-provenance.md)
