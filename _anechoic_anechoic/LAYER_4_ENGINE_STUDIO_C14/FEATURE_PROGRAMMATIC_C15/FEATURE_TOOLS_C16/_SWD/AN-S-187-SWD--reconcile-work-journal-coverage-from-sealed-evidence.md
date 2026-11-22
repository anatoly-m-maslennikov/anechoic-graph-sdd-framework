---
atom_family: SPEC
atom_id: AN-S-187
container:
  component: C16
tier: 2
context:
  lens: SWD
state:
  status: active
  version: 18
  updated_at: 2026-11-02 19:44:26 +0400
---
## Summary

Reconcile Work Journal coverage from sealed evidence

# Reconcile Work Journal coverage from sealed evidence

## Applicable when

use this Method **when** a governed action **may** be missing required Work Journal coverage.

## Procedure

1. seal one governed action frontier **and** collect its action identity, authoritative state, reachable provenance, existing Journal events, **and** the active Journal-event schema.
2. determine whether the existing events provide the coverage required for that exact action.
3. classify absent, duplicate, partial, stale, **or** conflicting coverage **without** editing existing Journal lines.
4. append one `recovered` event **only** **when** sealed durable evidence determines **every** schema-required event field **and** its action binding unambiguously.
5. re-run the same reconciliation on the unchanged frontier **and** confirm that it appends no second recovered event.

## Outcome

**every** selected governed action has an explicit coverage state: covered, recovered from sufficient evidence, **or** blocked for operator resolution.

## Failure or stop

never invent a schema-required event fact, action binding, **or** provenance fact; preserve insufficient cases as blocked.
