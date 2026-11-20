---
atom_family: TKT
atom_id: AN-T-1579
structure:
  container:
    atom: AN-T-1597
  priority: 2
context:
  template: task
state:
  status: done
  version: 9
  updated_at: 2026-10-25 17:32:27 +0400
---
# Summary

Specify Project selection for the MCP launcher

## Objective

the AI Agent defines the Project-selection contract for the Python launcher so the selected ANECHOIC Framework Instance is unambiguous **before** runtime effects.

## Details

- input: the approved launcher design, Project Settings, Project Structure, **and** existing authority **in** `.anechoic_anechoic/102_LAYER_2_FRAMEWORK_ENGINE/201_FEATURE_PROGRAMMATIC/203_FEATURE_APPS/WORKFLOW_ORCHESTRATOR` **and** `.anechoic_anechoic/102_LAYER_2_FRAMEWORK_ENGINE/201_FEATURE_PROGRAMMATIC/204_FEATURE_MCP`.
- output: reviewed source RMED for the explicit Project root path **and** its directly contained `.anechoic_<project>` settings/control folder, canonical instance identity, permitted mounts, **and** per-Project runtime state, including MCP reload receipts, pending work, **and** caches. separate Project roots can share a repository; image build sources are independent. reuse existing authority rather than duplicate it.
- verification: compare the contract with separate-repository **and** same-repository Project examples; reject ambiguous selection **without** choosing another Project.
- effort: **`<=15`** minutes for **`=1`** AI Agent; the Epic's decomposition rule applies **before** execution **if** the estimate no longer holds.

### Definition of Done

- completion evidence: R1900, M355, E599, D593 source contract; independent launcher_security review passed the explicit Project-root, no-Git-precondition, selected-mount, identity, ambiguity, authority **and** state boundaries.

the Plan is **not** Done **if** ((the selected Project cannot be resolved uniquely from the specified inputs) **or** (same-repository instance identity **and** state boundaries are unspecified) **or** (the source contract has no recorded independent review)).
