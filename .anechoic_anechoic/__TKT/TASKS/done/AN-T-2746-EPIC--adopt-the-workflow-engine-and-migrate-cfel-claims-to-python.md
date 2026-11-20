---
identity:
  atom_id: AN-T-2746
context:
  container:
    component: C14
  tier: 3
  template: epic
state:
  status: done
  version: 1
  updated_at: '2026-11-12T01:46:36+00:00'
---
## Summary

Adopt the Workflow Engine and migrate CFEL Claims to Python

## Objective

Adopt Python for Workflow business logic and Model Formal Claims. Retire CFEL entirely from the active ANECHOIC specification, build and runtime. Preserve existing Topic notation and Subject resolution while moving surviving Relation and Format addresses out of the CFEL branch.

## Work

1. Compare the Current Atom Lifecycle O Atoms with the code in CA-P-3019. Adopt the Workflow Engine RMED in CA-P-3020 and verify the Python Workflow pilot in CA-P-3021.
2. Finish the Python Claim migration in CA-P-3022. Convert surviving Current and Draft Claims, and verify their Model references and behavior.
3. In CA-P-3060, migrate Current and Draft Topic references to the surviving Model addresses. Remove the CFEL-only specifications and Declarations from the live Model.
4. In CA-P-3061, move all remaining readers to native Python Claims or the generated Model. Remove CFEL parsers, translators, build hooks and runtime dependencies.

## Definition of Done

- CA-P-3022, CA-P-3060 and CA-P-3061 are Done.
- The authoritative Current and Draft sources contain no CFEL Formal Claims or Topic references to the retired CFEL branch. Archived revisions remain available as history.
- The build and runtime have zero CFEL dependencies, including Python-to-CFEL translation. The generated Model, Claim linter, Lifecycle, Workbench and Subject projections pass their checks on the replacement image. Verify the image after cutover.

## Verification

- CA-P-3021 matched four Lifecycle baseline scenarios and passed the packaged API and MCP checks. Wave 46 ran the Python status Workflow tests in its release gate.
- Wave 46 published CA-R-1498@19 and archived @18. Its publication verifier matched the Model graph and six compiler outputs. Workbench query `618dc18ac96b4daf9d76f6068ef59770` confirmed that @19 is Current with a Python Formal Claim.
