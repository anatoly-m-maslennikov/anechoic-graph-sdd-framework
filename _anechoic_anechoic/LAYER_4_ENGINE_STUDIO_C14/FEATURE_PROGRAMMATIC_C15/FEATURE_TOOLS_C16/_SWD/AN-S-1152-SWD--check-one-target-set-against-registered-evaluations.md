---
atom_family: SPEC
atom_id: AN-S-1152
container:
  component: C16
tier: 2
context:
  lens: SWD
state:
  status: active
  version: 23
  updated_at: "2026-11-27T16:29:34.309627+00:00"
---
## Summary

Check one target set against registered Evaluations

# Check one target set against registered Evaluations

## Applicable when

use this Method **when** `GRAPH_CHECK` **must** apply selected registered Evaluation criteria **to** one previously sealed target set.

## Procedure

1. Verify the `GRAPH_CHECK` registration against AN-S-1182.
2. resolve one sealed target-set identity **and** selected registered Evaluation criteria.
3. confirm that the target set retains its recorded membership, source frontier, **and** digest **before** beginning evaluation.
4. apply **every** selected criterion **to** **every** applicable target **and** retain attributable issue, evidence, **and** verdict records **in** deterministic target-and-criterion order.
5. distinguish satisfied, unsatisfied, inapplicable, blocked, **and** error verdicts, **and** return the complete result **without** changing governed Atoms, Journals, native Implementation, **or** derived outputs.

## Outcome

one read-only `GRAPH_CHECK` result provides stable attributable issues, evidence, **and** verdicts for the selected registered criteria over one sealed target set.

## Failure or stop

do **not** evaluate a stale **or** unresolved target set **and** do **not** mutate **any** governed carrier; return explicit blocked **or** error verdicts instead.
