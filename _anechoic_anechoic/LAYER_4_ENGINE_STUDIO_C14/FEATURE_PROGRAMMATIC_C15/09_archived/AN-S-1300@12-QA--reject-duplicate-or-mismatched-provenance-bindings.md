---
atom_family: SPEC
atom_id: AN-S-1300
container:
  component: C15
tier: 1
context:
  lens: QA
state:
  status: archived
  version: 12
  updated_at: 2026-10-24 02:14:24 +0400
---
## Summary

Reject duplicate or mismatched provenance bindings

# Reject duplicate or mismatched provenance bindings

## Claim checked

one sealed action cannot become reconciled while duplicate canonical records,
duplicate real-change commits, **or** revision **or** digest mismatches remain.

## Test case

provide one sealed action with two Journal records that both claim canonical
binding **to** the same real-change commit.

## Acceptance criteria

pass **only** **when** reconciliation detects the duplicate, returns an explicit
blocked state, **and** does **not** select one record by guesswork.

## Failure disposition

preserve the discrepancy **and** block provenance reliance **until** deterministic
repair establishes one binding.

## Sources

- [CA-M-192 — Reconcile independent Git and Journal provenance](../05_method/CA-M-192-PROGRAMMATIC-METHOD--reconcile-independent-git-and-journal-provenance.md)
