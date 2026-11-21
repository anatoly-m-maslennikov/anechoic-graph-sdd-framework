---
atom_family: SPEC
atom_id: AN-S-1920
structure:
  container:
    component: C15
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 23
  updated_at: '2026-11-12T01:59:14.433341+00:00'
---
## Summary

Bind each programmatic mutation to one Initiative

## Claim

### Prose Claim

Every accepted programmatic mutation governed by Initiative binding must belong **to** **=1** sealed Initiative **and** one stable action identity. The Initiative **may** reference a persisted Plan **or** Task Atom **or** an ephemeral session task, **and** **must** retain a short summary derived from the human instruction plus sufficient structured context **to** identify that instruction **without** inventing a governed Plan Atom.

The six direct Project Atom Lifecycle Tools follow the specific contract in CA-R-1105.

the sealed Initiative **and** action identity **must** survive asynchronous handoffs, retries, concurrent workers, Git commits, Journal records, **and** reconciliation. A worker **must not** replace them with a process, thread, adapter, **or** queue parent identity.

