---
atom_family: SPEC
atom_id: AN-S-2779
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 15
  updated_at: 2026-10-24 12:35:51 +0400
---
## Summary

Separate methodology and Tool Evaluation responsibilities

# Summary

Separate methodology and Tool Evaluation responsibilities

## Scope

Evaluation responsibility for operational definitions and their Tool implementations.

## Claim

**in** the ANECHOIC Project, Evaluation responsibility for operational definitions **and** their Tool implementations **must** follow this allocation:

## Details

- methodology source Scope Units own Evaluations of Action **and** Workflow definitions, including valid Action references, Step inputs, typed transitions, **and** termination **or** bounded retry conditions. these Evaluations **may** directly check O authority under CA-R-1018; checks for Steps **and** Runs reuse CA-E-486 **when** applicable.
- TOOLS **and** its Tool Scope Units own Evaluations of Tools: implementation behavior, interfaces, failures, **and** conformance **to** the Action implemented by the Tool. these Evaluations **must not** independently define the correctness rules of the referenced Action **or** Workflow.

checking whether a Tool realizes an Action correctly is distinct from checking whether that Action's definition is valid. a Tool test **may** use the methodology definition as its expected-behavior authority **without** taking ownership of definition validation.
