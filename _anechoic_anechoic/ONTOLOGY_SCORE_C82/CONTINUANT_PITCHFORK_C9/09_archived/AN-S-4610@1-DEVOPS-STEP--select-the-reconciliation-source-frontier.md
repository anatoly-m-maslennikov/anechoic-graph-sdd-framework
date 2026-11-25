---
atom_family: SPEC
atom_id: AN-S-4610
container:
  component: C9
tier: 3
context:
  template: step
  lens: DevOps
state:
  status: archived
  version: 1
  updated_at: 2026-10-04 17:42:12 +0000
---
## Summary

Select the reconciliation source frontier

# Summary

Select the reconciliation source frontier

## Operation

Source Reconciliation Selection Step **means** the node **in** Workflow `CA-O-010` invoking **`=1`** Action, `CA-O-004`.

- bind the requested source selection **and** applicable source authority from the admitted Workflow Run inputs. retain the exact proposal, decision **and** source-frontier bindings supplied for this invocation, **when** applicable, rather than independently selecting **or** inferring them.
- for an Agentic invocation, use Integrated context under `CA-R-1527-CORE_META_MODEL-GENERAL-REQUIREMENT--define-agentic-step-execution-context`; this does **not** grant additional authority. a Programmatic invocation does **not** acquire an Agent context. missing required context **or** capability returns a blocked invocation rather than silent substitution.
- retain exact Action/Step Revisions, input/source bindings, actual effects **and** returned results for the Step Run. pass the Action's unchanged result **and** payload **to** the Workflow **without** copying **or** redefining its behavior.
- remain within the Workflow's applicable approval, currentness, confidence, accepted revisit/recovery allowance **and** escalation guards. this Step does **not** authorize an extra retry, correction, publication, **or** decision.

## Details
