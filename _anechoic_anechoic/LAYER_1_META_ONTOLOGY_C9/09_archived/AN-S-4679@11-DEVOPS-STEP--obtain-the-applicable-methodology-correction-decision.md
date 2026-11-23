---
atom_family: SPEC
atom_id: AN-S-4679
container:
  component: C9
tier: 3
context:
  template: step
  lens: DevOps
state:
  status: archived
  version: 11
  updated_at: 2026-10-24 00:38:25 +0400
---
## Summary

Obtain the Applicable Methodology correction decision

# Summary

Obtain the Applicable Methodology correction decision

## Operation

this Step is the decide node **of** CA-O-011, Applicable Methodology Compilation, invoking **`=1`** Action, CA-O-007, Obtain Source Correction Decision.

### Inputs and parameters

bind the exact proposal from CA-O-154, conflict and source-frontier digest from CA-O-153, and the Workflow Run's required Operator decision context with independently retained execution evidence.

enforce CA-R-1317 through CA-O-007: obtain **`=1`** unambiguous current actual Operator decision bound **to** the exact proposal, conflict, **and** source-frontier digest, and independently retain **and** verify it through admitted execution evidence. the Journal append is a business-provenance attempt; failure yields a `recording_error` diagnostic and does **not** qualify or disqualify the decision, block dispatch, **or** serve as proof, permission, completion, **or** recovery gate. stale, partial, missing, ambiguous, **or** mismatched decision does **not** qualify. do **not** create an approval Atom **in** Project Configuration; approval **must not** itself bypass Core expansion boundaries.

### Agentic invocation binding

for an invocation whose actual bound Action is Agentic, bind **`=1`** Integrated **or** Isolated context under CA-R-1527 from the admitted invocation's supplied `agentic_execution_context` runtime parameter **before** dispatch. missing, ambiguous **or** unsupported values, **or** unavailable required context/capability, block that Agentic invocation; do **not** default **or** silently substitute. retain the selected context with the Step Run. a Programmatic invocation does **not** acquire an Agent context **or** require this parameter. this binding grants no additional authority **and** does **not** change the Action's identity **or** behavior.

## Details
