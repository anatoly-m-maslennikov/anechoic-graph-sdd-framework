---
atom_family: SPEC
atom_id: AN-S-5175
container:
  component: C16
tier: 2
context:
  lens: DevOps
state:
  status: active
  version: 1
  updated_at: '2026-11-27T17:35:02.223516+00:00'
---

## Summary

Accept one immutable COMMIT_TRIGGER event

## Claim

the launcher validates **and** normalizes the host payload into one immutable schema-versioned event **and** atomically renames it into .anechoic_runtime/state/commit_automation/inbox/<event_id>.json. The event records source, repository, session, turn, Tool-use, Hook event, stable event identity, observation time, **and** candidate changed targets available from the payload. Repeated event identity is idempotent. Concurrent **and** out-of-order callbacks write independent events. Intake returns **after** durable acceptance **and** performs no repository scan, graph traversal, before-event snapshot, context gathering, Journal append, Git mutation, retry, lifecycle control, **or** direct worker spawn.
