---
atom_family: SPEC
atom_id: AN-S-4675
container:
  component: C9
tier: 3
context:
  template: step
  lens: DevOps
state:
  status: archived
  version: 12
  updated_at: 2026-10-27 19:59:46 +0400
---
## Summary

Construct the requested Terms Graph

# Summary

Construct the requested Terms Graph

## Operation

Terms Graph Construction Step **means** the node of CA-O-136 invoking **=1** Action, CA-O-137, with graph kind fixed **to** Terms Graph.

- bind the Action's admitted request, exact source selection, narrower/governed-only view selection **if** any, current authoritative source set, governing Term/Relation Kind authority, representation configuration, target Projection/output destination **and** existing Projection/evidence from the corresponding Workflow invocation inputs.
- bind permissions, admitted realization/execution kind **and** recording context from that invocation's current admitted execution context. retain actual Workflow/Step/Action definition Revisions **and** actual Run/parent references; no earlier completed Run **or** projected state supplies missing inputs.
- resolve execution kind under CA-R-1526. for an Agentic invocation, bind **=1** Integrated **or** Isolated context from the explicitly supplied Workflow runtime parameter under CA-R-1527; for Programmatic execution, no Agent context is selected. missing input, capability, permission **or** Agentic context blocks dispatch rather than silent substitution.
- return the Action's exact result/effects/evidence **to** CA-O-136 **without** copying construction behavior, changing scope, repairing sources **or** turning internal Tool calls into Steps.

## Details

this reusable binding is distinct from its Step Run. separately placed Workflow/Step Carriers retain unambiguous references under CA-D-467.
