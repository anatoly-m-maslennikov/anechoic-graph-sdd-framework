---
atom_family: SPEC
atom_id: AN-S-1987
container:
  component: C21
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 6
  updated_at: 2026-10-23 03:17:34 +0400
---
## Summary

Delegate one Initiative-bound Atom mutation

# Delegate one Initiative-bound Atom mutation

## Applicable when

Apply **when** an authorized project-local MCP operation requests an Atom mutation.

## Procedure

1. Preserve the human-origin Initiative **and** select the one canonical Atom Tool **without** resolving its target **or** lifecycle meaning.
2. Forward the sealed request **to** that Tool **and** return its structured outcome unchanged.
3. Report success **only** **after** the canonical Tool returns its acknowledged outcome; preserve a rejection, conflict, partial result, **or** blocked result as such.

## Outcome

MCP transports one authorized mutation request **without** becoming the target, mutation, recovery, **or** success-state owner.

## Failure or stop

Stop **and** return an explicit failure **when** authorization, Initiative, canonical Tool selection, **or** the Tool outcome is absent **or** invalid.
