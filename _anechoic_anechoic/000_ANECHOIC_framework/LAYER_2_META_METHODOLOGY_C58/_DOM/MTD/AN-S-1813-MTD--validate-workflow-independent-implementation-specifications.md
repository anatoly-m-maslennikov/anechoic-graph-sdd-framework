---
atom_family: SPEC
atom_id: AN-S-1813
container:
  component: C58
tier: 3
context:
  lens: DOM/MTD
state:
  status: "active"
  version: 31
  updated_at: "2026-11-25T21:38:53.535562+00:00"
---
## Summary

Validate Workflow-independent Implementation specifications

## Claim

### Prose Claim


the Evaluation of a ANECHOIC implementation Spec.


the Evaluation of a ANECHOIC implementation Spec **must** reject dependence on a production Workflow under AN-S-2339.

## Cases and expected results

- the same RMED is satisfied by Implementations produced with different Workflows **or** **without** a formally defined Workflow: neither production choice is a failure by itself.
- an ordinary implementation Requirement delegates a required behavior **to** an O definition outside the permitted exceptions: fail for incomplete RMED authority.
- an implementation Spec requires a particular production Workflow as the condition for conformity: fail for coupling the result **to** its production procedure.
- a Tool's RMED refers **to** the methodology Action it implements under CA-R-1800-PROJECT_CONFIGURATION-RULE--bind-every-tool-to-one-methodology-action **and** AN-S-1793: this permitted realization reference is **not** a production-Workflow dependency.
- a methodology Evaluation checks an Action **or** Workflow definition under CA-R-1518-PROJECT_CONFIGURATION-RULE--separate-methodology-and-tool-evaluation-responsibilities: this permitted evaluation target is **not** a production-Workflow dependency.
- a generic executor consumes different applicable Workflow definitions as inputs while its RMED fully specifies their interpretation under AN-S-1614: accept this boundary; reject an attempt **to** treat a particular production Workflow as necessary for executor conformity.
- changing a valid Workflow input changes the executed behavior **without** requiring a copied Workflow policy **in** the executor Spec: this is input interpretation, **not** incomplete implementation authority.

identify the exact Claim, reference, **and** violated boundary. incomplete evidence **must not** be reported as a pass.
