---
atom_family: SPEC
atom_id: AN-S-2339
container:
  component: C9
tier: 2
context:
  lens: DES
state:
  status: archived
  version: 16
  updated_at: 2026-10-24 12:35:51 +0400
---
## Summary

Keep Implementation specifications independent of production Workflows

# Summary

Keep Implementation specifications independent of production Workflows

## Scope

the ANECHOIC Project's governing RMED for an Implementation.

## Claim

**in** the ANECHOIC Project, governing RMED **must** fully specify the required Implementation independently of the Workflow used **to** produce it.

## Details

- conformity depends on the resulting Implementation satisfying its RMED, **not** on following a particular production Workflow. different Workflows, **or** work **without** a formally defined Workflow, **may** produce a conforming Implementation.
- ordinary implementation RMED **must not** leave required behavior specified **only** **in** an O Atom **or** require an O Atom as its production procedure.
- the permitted authority references are the Tool realization binding under CA-R-1516-PROJECT_CONFIGURATION-REQUIREMENT--bind-each-tool-to-one-methodology-action **and** CA-R-1517-PROJECT_CONFIGURATION-RULE--keep-tool-operational-authority-outside-its-own-subtree, **and** methodology checks of Action **and** Workflow definitions under CA-R-1518-PROJECT_CONFIGURATION-RULE--separate-methodology-and-tool-evaluation-responsibilities. neither exception makes the Workflow used **to** build the Implementation part of its specification.
- a generic executor **may** consume applicable O definitions as runtime inputs under CA-R-1519-CORE_META_MODEL-RULE--require-conforming-workflow-execution. its RMED **must** fully specify how it interprets those inputs; the selected Workflow is **not** its production procedure **or** an independently copied part of its Spec.

these are ANECHOIC Project Configuration boundaries, **not** a change **to** the reusable Core Meta-Model Content Roles.
