---
atom_family: SPEC
atom_id: AN-S-1732
container:
  component: C9
tier: 3
context:
  lens: QA
state:
  status: archived
  version: 10
  updated_at: 2026-10-23 03:06:32 +0400
---
## Summary

Validate Workflow Steps and Runs

# Summary

Validate Workflow Steps and Runs

## Scope

Workflow Steps **and** Runs.

## Claim

the Evaluation **must** check Workflow Steps **and** Runs.

## Details

### Cases

- define **`=2`** distinct Steps referencing the same Action with different input bindings; follow an admitted conditional transition between the Steps.
- revisit a Step under an accepted retry allowance within **`=1`** Workflow Run.
- introduce a Step with **`=0`** Action references, **`>1`** Action references, an unresolved Action, **or** an unresolved required input binding.
- introduce an untyped edge, an edge whose endpoint is an Action rather than a Step, **or** a next-Step reference missing from that Workflow.
- record a failed Step Run; separately reference a reusable Workflow definition **without** recording an execution.

### Acceptance

- the valid shared Action retains **`=1`** definition; Step bindings remain distinct.
- **every** actual revisit creates a distinct Step Run within the same Workflow Run **without** resetting its retry allowance.
- invalid Action cardinality, unresolved inputs, invalid endpoints, **and** untyped transitions fail the check.
- failed **or** absent execution evidence **must not** become successful completion, a new Workflow definition, **or** another historical source.

report the exact failing source, case, **and** condition; do **not** change source authority **to** make the check pass.
