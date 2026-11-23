---
atom_family: SPEC
atom_id: AN-S-251
container:
  component: C16
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 20
  updated_at: 2026-10-24 00:51:05 +0400
---
## Summary

Append all related Journal records independently of commit timing

# Append all related Journal records independently of commit timing

## Claim checked

the Journal Doer completes **every** related append independently of real-change commit timing **and** **without** using the repository Git gate for the append itself.

## Test case

start two valid actions for the same repository whose related records span disjoint **and** shared Journal carriers. **in** separate runs, complete Journal append **before**, during, **and** **after** the corresponding real-change commit; **then** commit the completed records **in** a later Journal-only batch.

## Acceptance criteria

disjoint Journal partitions **may** append concurrently. **every** shared carrier has one canonical writer **or** batcher, **every** accepted record is durable **and** idempotent, **and** no Journal append acquires the repository Git gate. real-change commits do **not** wait for Journal receipts. the later Journal-only commit **contains** **all** **and** **only** its selected Journal Carriers **and** shares the single fenced commit gate.

## Failure disposition

reject the flow **if** Journal timing gates the real-change commit, an append is lost **or** duplicated, writers race on one shared carrier, Journal append uses the Git gate, **or** either commit class **contains** the other's files.
