---
atom_family: SPEC
atom_id: AN-S-1301
container:
  component: C15
tier: 1
context:
  lens: QA
state:
  status: archived
  version: 16
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Separate action creation from provenance reliance

# Separate action creation from provenance reliance

## Claim checked

one action **may** complete its originating mutation while provenance is pending,
but a later release **or** promotion-dependent action cannot rely on it **before**
reconciliation.

## Test case

complete one mutation into `git_complete_journal_pending`, **then** request a later
release that depends on that action's provenance.

## Acceptance criteria

pass **only** **when** the originating mutation remains complete **and** the later release
is blocked **until** the action becomes `reconciled`.

## Failure disposition

reject either behavior that blocks the originating mutation on its own pending
state **or** permits later governed reliance **before** reconciliation.

## Sources

- [CA-M-192 — Reconcile independent Git and Journal provenance](../05_method/CA-M-192-PROGRAMMATIC-METHOD--reconcile-independent-git-and-journal-provenance.md)
