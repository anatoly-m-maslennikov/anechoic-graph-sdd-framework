---
atom_family: SPEC
atom_id: AN-S-1909
container:
  component: C15
tier: 4
context:
  lens: SWD
state:
  status: "active"
  version: 16
  updated_at: "2026-11-27T20:35:14.221449+00:00"
---

## Summary

Separate deterministic transformations from effects and lifecycle

## Claim

### Prose Claim

Make PROGRAMMATIC decisions in a deterministic core under AN-S-1897.

Apply filesystem, process, clock, environment, network, persistence and logging-export effects through a specifically named, bounded one-shot function or a specifically named method on the owning object. Use AN-S-1898 to determine when the effect requires an object.

## Details

### Applicable when

Apply when a Tool, App backend service, or MCP component combines a decision with an external effect, asynchronous work, or a lifecycle transition.

### Procedure

1. Use explicit observations to form the decision, target, order and expected outcome before applying an effect.
2. Pass the plan to one bounded effect boundary. For a one-shot function, make its complete target, dependencies, input, outcome and failure boundary explicit.
3. Return typed observations or completion facts to the decision boundary. The effect owner must apply the plan without inventing, reordering or suppressing a decision.

### Outcome

The decision logic is locally readable and replayable. Each effect has a visible owner, ordered input and a recoverable result boundary.

### Failure or stop

Stop if the plan is incomplete, the effect owner would make a new business decision, a one-shot effect hides a dependency or exceeds its declared boundary, or the effect boundary cannot report a typed result.

### Sources

- [Python Functional Programming HOWTO](https://docs.python.org/3.14/howto/functional.html)
- [Python documentation: data classes](https://docs.python.org/3.14/library/dataclasses.html)
- [CA-A-053 — Reconcile shared PROGRAMMATIC policy decisions](../02_analysis_and_advisory/CA-A-053-PROGRAMMATIC-ANALYSIS_RPRT--reconcile-shared-programmatic-policy-decisions.md)

### Pure computation and execution recording

Keep pure computation independent of persistence and Run or Journal writes. Construct results and diagnostics from bound inputs without hidden writes. Persist an output only through its declared authorized effect boundary. Actual execution recording remains with its declared executor; generated output alone does not establish durable terminal completion.
