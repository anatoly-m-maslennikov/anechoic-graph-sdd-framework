---
atom_family: SPEC
atom_id: AN-S-1139
container:
  component: C16
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 9
  updated_at: 2026-10-24 00:28:02 +0400
---
## Summary

Reconcile Git and Journal provenance bidirectionally

# Reconcile Git and Journal provenance bidirectionally

## Applicable when

use this Method **when** comparing reachable Git change history with Work Journal coverage for the same governed action frontier.

## Procedure

1. seal a reachable Git frontier **and** the corresponding Journal batch frontier.
2. normalize both sides **to** action, Initiative, commit SHA, event ID, subject path, subject revision, digest, batch SHA, **and** ordering facts.
3. match Git real-change commits **to** Journal events **in** both directions **and** classify missing, duplicate, unreachable, digest-mismatched, revision-mismatched, **and** watermark-lag cases.
4. append a recovered Journal event **only** **when** reachable history **and** sealed durable state prove **every** required field; **otherwise** keep the case blocked.
5. re-run the comparison over the same frontier **and** emit a stable reconciliation report whose second unchanged run produces no new events.

## Outcome

Git **and** Journal provenance are either reconciled idempotently **or** separated into explicit evidence-backed discrepancy classes.

## Failure or stop

do **not** infer missing provenance **or** rewrite Git history; stop recovery whenever required identity, digest, reachability, **or** batch evidence is insufficient.
