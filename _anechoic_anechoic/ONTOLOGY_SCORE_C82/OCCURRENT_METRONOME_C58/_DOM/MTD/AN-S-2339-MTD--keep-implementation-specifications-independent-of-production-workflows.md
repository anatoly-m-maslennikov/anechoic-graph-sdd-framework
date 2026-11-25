---
atom_family: SPEC
atom_id: AN-S-2339
container:
  component: C58
tier: 2
context:
  lens: DOM/MTD
state:
  status: "active"
  version: 30
  updated_at: "2026-11-25T21:38:53.297385+00:00"
---
## Summary

Keep Implementation specifications independent of production Workflows

## Claim

### Prose Claim


the ANECHOIC Project's governing RMED for an Implementation.


**in** the ANECHOIC Project, governing RMED **must** fully specify the required Implementation independently of the Workflow used **to** produce it.

## Details

- conformity depends on the resulting Implementation satisfying its RMED, **not** on following a particular production Workflow. different Workflows, **or** work **without** a formally defined Workflow, **may** produce a conforming Implementation.
- ordinary implementation RMED **must not** leave required behavior specified **only** **in** an O Atom **or** require an O Atom as its production procedure.
- the permitted authority references are the Tool realization binding under CA-R-1800-PROJECT_CONFIGURATION-RULE--bind-every-tool-to-one-methodology-action **and** AN-S-1793, **and** methodology checks of Action **and** Workflow definitions under CA-R-1518-PROJECT_CONFIGURATION-RULE--separate-methodology-and-tool-evaluation-responsibilities. neither exception makes the Workflow used **to** build the Implementation part of its specification.
- a generic executor **may** consume applicable O definitions as runtime inputs under AN-S-1614. its RMED **must** fully specify how it interprets those inputs; the selected Workflow is **not** its production procedure **or** an independently copied part of its Spec.

these are ANECHOIC Project Configuration boundaries, **not** a change **to** the reusable Core Meta-Model Content Roles.
