---
atom_family: SPEC
atom_id: AN-S-1909
container:
  component: C15
tier: 4
context:
  lens: SWD
state:
  status: archived
  version: 14
  updated_at: 2026-11-09 14:19:14 +0400
---

## Summary

Separate deterministic transformations from effects and lifecycle

## Claim

### Prose Claim

keep PROGRAMMATIC decisions **in** a function-based deterministic core. apply
filesystem, process, clock, environment, network, persistence, **or**
logging-export effects through a specifically named bounded one-shot function
**when** no identity **or** ownership is required, **or** through a specifically named
method on an object that owns state, an invariant, a resource, a lifecycle, **or**
a replaceable adapter.

## Details

Candidate source: [CA-M-160@12](archive/CA-M-160-PROGRAMMATIC-CORE-METHOD--separate-deterministic-transformations-from-effects-and-lifecycle@12.md)

### Applicable when

apply **when** a Tool, App backend service, **or** MCP component combines a decision
with an external effect, asynchronous work, **or** lifecycle transition.

### Procedure

1. form the decision, target, ordering, **and** expected outcome with deterministic
   functions from explicit observations **before** applying an effect.
2. pass the resulting plan **to** one bounded effect boundary.
3. use a function for a one-shot effect **only** **when** its complete target,
   dependency, input, outcome, **and** failure boundary are explicit **and** it owns
   no identity across calls, state, invariant, resource, lifecycle, **or** adapter.
4. use a specifically named object method **when** the effect **must** own **any** of those
   responsibilities across calls.
5. return typed observations **or** completion facts **to** the decision boundary;
   do **not** let the effect owner invent, reorder, **or** suppress a decision.

### Outcome

decision logic is locally readable **and** replayable. **every** effect has a visible,
bounded function **or** object owner, ordered input, **and** recoverable result
boundary. objects exist **only** **where** persistent identity **or** ownership requires
them.

### Failure or stop

stop execution **when** the plan is incomplete, an effect owner would make a new
business decision, a one-shot effect hides a dependency **or** exceeds its declared
boundary, an object exists **without** owned identity **or** ownership, **or** the effect
boundary cannot report a typed result.

### Sources

- [Python Functional Programming HOWTO](https://docs.python.org/3.14/howto/functional.html)
- [Python documentation: data classes](https://docs.python.org/3.14/library/dataclasses.html)
- [CA-A-053 — Reconcile shared PROGRAMMATIC policy decisions](../02_analysis/CA-A-053-PROGRAMMATIC-ANALYSIS_RPRT--reconcile-shared-programmatic-policy-decisions.md)

### Pure computation and execution recording

Keep pure computation independent of persistence and Run or Journal writes. Construct results and diagnostics from bound inputs without hidden writes. Persist an output only through its declared authorized effect boundary. Actual execution recording remains with its declared executor; generated output alone does not establish durable terminal completion.
