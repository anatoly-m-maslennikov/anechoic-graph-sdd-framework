---
atom_family: SPEC
atom_id: AN-S-1987
container:
  component: C21
tier: 2
context:
  lens: SWD
state:
  status: archived
  version: 21
  updated_at: 2026-11-11 14:19:47 +0400
---

## Summary

Delegate one Initiative-bound Atom mutation

## Claim

### Prose Claim

#### Applicable when

Apply **when** an Initiative-bound project-local MCP operation requests an Atom mutation. For the six Atom Lifecycle Tools, forward the request and selected Project to the runtime backend under CA-R-1105.

#### Procedure

1. Preserve the human-origin Initiative **and** select the one canonical Atom Tool **without** resolving its target **or** lifecycle meaning.
2. Forward the sealed request **to** that Tool **and** return its structured outcome unchanged.
3. Report success **only** **after** the canonical Tool returns its acknowledged outcome; preserve a rejection, conflict, partial result, **or** blocked result as such.

#### Outcome

MCP transports one authorized mutation request **without** becoming the target, mutation, recovery, **or** success-state owner.

#### Failure or stop

Stop **and** return an explicit failure **when** authorization, Initiative, canonical Tool selection, **or** the Tool outcome is absent **or** invalid.
