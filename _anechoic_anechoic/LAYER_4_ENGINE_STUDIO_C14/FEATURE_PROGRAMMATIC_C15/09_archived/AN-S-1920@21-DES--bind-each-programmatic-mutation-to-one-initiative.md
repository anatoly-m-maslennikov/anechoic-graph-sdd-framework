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
  version: 21
  updated_at: 2026-11-09 00:09:26 +0400
---
## Summary

Bind each programmatic mutation to one Initiative

## Claim scope

## Claim

### Prose Claim

**every** accepted programmatic mutation **must** belong **to** **=1** sealed Initiative **and** one stable action identity. The Initiative **may** reference a persisted Plan **or** Task Atom **or** an ephemeral session task, **and** **must** retain a short summary derived from the human instruction plus sufficient structured context **to** identify that instruction **without** inventing a governed Plan Atom.

the sealed Initiative **and** action identity **must** survive asynchronous handoffs, retries, concurrent workers, Git commits, Journal records, **and** reconciliation. A worker **must not** replace them with a process, thread, adapter, **or** queue parent identity.

## Details
