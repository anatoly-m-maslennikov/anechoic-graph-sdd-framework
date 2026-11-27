---
atom_family: SPEC
atom_id: AN-S-1139
concern:
  subject: "Event Record"
  path: "Model/Graph/Node//Artifact//SSOT//Recorded"
  relation: "is_narrower_than"
container:
  component: C16
tier: 2
context:
  lens: SWD
state:
  status: active
  version: 19
  updated_at: "2026-11-27T16:29:34.309627+00:00"
---
## Summary

Reconcile Git and Journal provenance bidirectionally

# Reconcile Git and Journal provenance bidirectionally

## Applicable when

use this Method **when** comparing reachable Git change history with Work Journal coverage for the same governed action frontier.

## Procedure

1. seal a reachable Git frontier **and** the corresponding Journal batch frontier.
2. normalize both sides **to** action, Initiative, commit SHA, event ID, subject path, subject revision, digest, batch SHA, **and** ordering facts.
3. Match in both directions and classify and recover discrepancies under AN-S-1163.
4. Re-run the comparison over the same frontier and emit a stable report. An unchanged run creates no events.

## Outcome

Git **and** Journal provenance are either reconciled idempotently **or** separated into explicit evidence-backed discrepancy classes.

## Failure or stop

do **not** infer missing provenance **or** rewrite Git history; stop recovery whenever required identity, digest, reachability, **or** batch evidence is insufficient.
