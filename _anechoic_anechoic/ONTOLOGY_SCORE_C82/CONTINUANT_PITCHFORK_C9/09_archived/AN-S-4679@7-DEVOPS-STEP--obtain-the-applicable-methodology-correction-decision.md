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
  version: 7
  updated_at: 2026-10-19 15:56:34 +0400
---
## Summary

Obtain the Applicable Methodology correction decision

# Summary

Obtain the Applicable Methodology correction decision

## Operation

this Step is the decide node **of** CA-O-011, Applicable Methodology Compilation, invoking **`=1`** Action, CA-O-007, Obtain Source Correction Decision.

### Inputs and parameters

bind the exact proposal from CA-O-154, conflict and source-frontier digest from CA-O-153, and the Workflow Run's required Operator approval context and canonical Journal reference.

enforce CA-R-1317 through CA-O-007: obtain **`=1`** unambiguous actual Operator approval **and** record it **in** the Journal, bound **to** the exact proposal, conflict, **and** source-frontier digest. stale, partial, missing, ambiguous, **or** mismatched approval does **not** qualify. do **not** create an approval Atom **in** Project Configuration; approval **must not** itself bypass Core expansion boundaries.

### Agentic invocation binding

for an invocation whose actual bound Action is Agentic, bind **`=1`** Integrated **or** Isolated context under CA-R-1527 from the admitted invocation's supplied `agentic_execution_context` runtime parameter **before** dispatch. missing, ambiguous **or** unsupported values, **or** unavailable required context/capability, block that Agentic invocation; do **not** default **or** silently substitute. retain the selected context with the Step Run. a Programmatic invocation does **not** acquire an Agent context **or** require this parameter. this binding grants no additional authority **and** does **not** change the Action's identity **or** behavior.

## Details
