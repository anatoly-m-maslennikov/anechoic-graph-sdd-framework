---
atom_family: SPEC
atom_id: AN-S-1920
container:
  component: C15
tier: 3
context:
  lens: DES
state:
  status: archived
  version: 14
  updated_at: 2026-10-24 01:37:42 +0400
---
## Summary

Bind each programmatic mutation to one Initiative

# Summary

Bind each programmatic mutation to one Initiative

## Scope

## Claim

**every** accepted programmatic mutation **must** belong **to** **=1** sealed Initiative **and** one stable action identity. The Initiative **may** reference a persisted Plan **or** Task Atom **or** an ephemeral session task, **and** **must** retain a short summary derived from the human instruction plus sufficient structured context **to** identify that instruction **without** inventing a governed Plan Atom.

the sealed Initiative **and** action identity **must** survive asynchronous handoffs, retries, concurrent workers, Git commits, Journal records, **and** reconciliation. A worker **must not** replace them with a process, thread, adapter, **or** queue parent identity.

## Details
