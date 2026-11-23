---
atom_family: SPEC
atom_id: AN-S-64
container:
  component: C16
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 25
  updated_at: 2026-10-27 19:59:29 +0400
---
## Summary

Accept one Codex event without host delay or loss

# Accept one Codex event without host delay or loss

## Claim checked

the asynchronous Codex PostToolUse carrier acknowledges **only** one atomic durable inbox event **and** performs no provenance pipeline work.

## Test case

configure the installed Hook with async: true, block the background service, invoke one supported Codex Tool, delay Hook completion around the atomic rename boundary, **then** end the host session **and** repeat concurrent **and** duplicate source-event deliveries.

## Acceptance criteria

the Tool result becomes available **without** waiting for Hook completion. one schema-valid immutable event exists **after** atomic acceptance even **when** the host session **then** ends. concurrent distinct events remain distinct, out-of-order completion is accepted, **and** a repeated stable identity is idempotent. Hook execution performs no repository scan, graph traversal, context gathering, Journal append, staging, Git mutation, retry, lifecycle mutation, **or** worker spawn.

## Failure disposition

reject intake **if** host dispatch waits for provenance work, an acknowledged event is absent, a duplicate effect exists, **or** **any** prohibited work occurs **in** the Hook process.
