---
atom_family: SPEC
atom_id: AN-S-1282
container:
  component: C15
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 9
  updated_at: 2026-09-01 02:00:00 +0400
---
## Summary

Verify bind one programmatic mutation to its initiative

# Verify bind one programmatic mutation to its initiative

## Claim checked

one accepted programmatic mutation preserves **=1** sealed Initiative **and**
one stable action identity through asynchronous handoffs **and** retry.

## Applicable conditions

apply **when** one accepted human instruction causes a programmatic mutation that
passes through a queue **or** worker boundary.

## Test case

create one sealed Initiative **and** action identity, dispatch the mutation through
one queue **and** worker, force one retry, **and** observe **every** handoff plus the final
mutation receipt.

## Acceptance criteria

pass **only** **when** **every** handoff **and** the final receipt retain the same Initiative
**and** action identities, while process, queue, worker, **and** retry identities remain
linked execution context **and** never replace them.

## Failure disposition

reject the mutation provenance **and** return the identity propagation boundary **to**
its owner **before** later reliance.

## Sources

- [CA-M-191 — Bind one programmatic mutation to its Initiative](../05_method/CA-M-191-PROGRAMMATIC-METHOD--bind-one-programmatic-mutation-to-its-initiative.md)
