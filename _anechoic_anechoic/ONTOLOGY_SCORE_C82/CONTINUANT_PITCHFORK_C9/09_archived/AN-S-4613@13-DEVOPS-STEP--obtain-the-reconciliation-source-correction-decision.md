---
atom_family: SPEC
atom_id: AN-S-4613
container:
  component: C9
tier: 3
context:
  template: step
  lens: DevOps
state:
  status: archived
  version: 13
  updated_at: 2026-10-26 05:59:45 +0400
---
## Summary

Obtain the reconciliation source correction decision

# Summary

Obtain the reconciliation source correction decision

## Operation

Source Reconciliation Decision Step **means** the node **in** Workflow `CA-O-010` invoking **`=1`** Action, `CA-O-007`.

- bind the exact proposal, conflicts, frontier, **and** required approval context from CA-O-148's proposal result, the retained assessment/selection results, **and** admitted Workflow Run approval inputs. retain the exact proposal, decision **and** source-frontier bindings supplied for this invocation, **when** applicable, rather than independently selecting **or** inferring them.
- for an invocation whose actual bound Action is Agentic, bind **`=1`** Integrated **or** Isolated context under `CA-R-1527-CORE_META_MODEL-GENERAL-REQUIREMENT--define-agentic-step-execution-context` from the admitted invocation's supplied `agentic_execution_context` runtime parameter **before** dispatch. missing, ambiguous **or** unsupported values, **or** unavailable required context/capability, return a blocked Agentic invocation; do **not** default **or** silently substitute. retain the selected context with the Step Run. this does **not** grant additional authority. a Programmatic invocation does **not** acquire an Agent context.
- retain exact Action/Step Revisions, input/source bindings, actual effects **and** returned results for the Step Run. pass the Action's unchanged result **and** payload **to** the Workflow **without** copying **or** redefining its behavior.
- remain within the Workflow's applicable approval, currentness, confidence, accepted revisit/recovery allowance **and** escalation guards. this Step does **not** authorize an extra retry, correction, publication, **or** decision.

## Details
