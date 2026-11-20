---
identity:
  atom_id: AN-S-1283
context:
  container:
    component: C15
  tier: 4
  lens: QA
state:
  status: active
  version: 22
  updated_at: 2026-11-10 20:47:54 +0400
---
## Summary

Verify reconcile independent git and journal provenance

## Claim



### Prose Claim
#### Claim checked

one action whose real-change Git commit completes **before** its Journal record
converges **to** one canonical reconciled cross-system binding.

#### Applicable conditions

apply **when** a sealed action is **in** `git_complete_journal_pending`.

#### Test case

create one reachable real-change commit for a sealed action, append **=1**
canonical Journal record bound **to** that commit, **then** commit the Journal carrier
**in** a later separate Git commit.

#### Acceptance criteria

pass **only** **when** the action becomes `reconciled`, **=1** canonical Journal
record binds **=1** reachable real-change commit, **and** the Journal record
does **not** embed the SHA of the commit containing that same record.

#### Failure disposition

keep the action pending **or** blocked, preserve its sealed state, **and** reject later
provenance reliance **until** reconciliation succeeds.

#### Sources

- [CA-M-192 — Reconcile independent Git and Journal provenance](../05_method/CA-M-192-PROGRAMMATIC-METHOD--reconcile-independent-git-and-journal-provenance.md)
