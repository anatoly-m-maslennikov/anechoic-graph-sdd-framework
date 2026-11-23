---
atom_family: SPEC
atom_id: AN-S-1188
container:
  component: C16
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 15
  updated_at: 2026-10-24 20:48:49 +0400
---
## Summary

Bound commit automation with an explicit autonomy envelope

# Bound commit automation with an explicit autonomy envelope

**every** autonomous `COMMIT_AUTOMATION` run **must** be admitted by one current, durable autonomy envelope. the envelope identifies its authorizing Work, repository, permitted subject scope, start **and** expiry **or** bounded execution window, permitted action kinds, queue **and** concurrency caps, resource **and** retry budgets, hard admission guards, circuit state, **and** the independent authority that **may** pause, resume, narrow, replace, **or** escalate it.

for the current ANECHOIC Tool surface, the **only** permitted Git action kinds are a local real-change commit **and** a local Journal-only commit. the envelope cannot admit branch, upstream, remote, synchronization, push, tag, release, **or** other Git effects. a broader request **must** stop for explicit Operator **or** external handling rather than widening the envelope.

the service **must** revalidate the envelope **before** admitting an action, **before** dispatching **every** effectful step, **and** immediately **before** commit creation. Missing Work linkage, ambiguity, expiry, exhausted caps, failed guards, stale authority, circuit opening, **or** scope escape pauses the affected work **before** the effect **and** preserves it for inspection **or** independently authorized recovery. the actor that authorizes **or** overrides an envelope **must** be distinct from the worker that executes its commit effect.

an envelope replacement **may** preserve **or** narrow already admitted work **only** **when** stable action identities **and** the still-valid original boundaries remain provable. Expansion, escalation, **or** resumption **after** an integrity failure requires an independently authorized new envelope.
