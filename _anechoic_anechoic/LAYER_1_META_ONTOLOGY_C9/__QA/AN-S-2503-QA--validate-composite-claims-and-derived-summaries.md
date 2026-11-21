---
atom_family: SPEC
atom_id: AN-S-2503
structure:
  container:
    component: C9
  tier: 3
context:
  lens: QA
state:
  status: active
  version: 43
  updated_at: '2026-11-13T18:45:59.062550+00:00'
---
## Summary

Validate Composite Claims and Derived Summaries

## Claim

### Prose Claim


the Claim boundary, applicability, supporting Details, **and** Summary of an Atom.


the Evaluation **must** reject an Atom **if** **any** applicable content-boundary condition fails:

- the Atom has **`!=1`** Claims, **`!=1`** resolved Claim Target Scope Units, an independently replaceable component inside **`=1`** Claim, ambiguous composite grouping, **or** a non-deterministic Scope Expression.
- RMED Scope is missing its applicability description, merely repeats the carried current **or** target Scope Unit, introduces a second independently replaceable Claim, **or** conflicts with the Claim. applicability **must** be explicit **in** Scope rather than maintained independently **in** Claim **or** Details.
- Details change, contradict, broaden, narrow, **or** add an independent contribution **to** the primary contribution within its applicability instead of expanding it under CA-R-2503-CORE_META_MODEL-DEFINITION--keep-details-within-the-primary-contribution.
- Summary is **not** source-faithful **to** the finalized primary contribution under CA-R-2499-CORE_META_MODEL-CORE-REQUIREMENT--define-summary-as-an-atom-property **and** CA-R-1273-CORE_META_MODEL-CORE-REQUIREMENT--keep-summary-source-faithful, including its applicability restrictions. for RMED, use the Claim read within Scope; a Summary of Scope alone fails. a Summary sourced from Analysis Results **or** TLDR instead of Question fails this check.

evaluate restrictions **to** selected sibling Scope Units under CA-E-461-CORE_META_MODEL-POLICY--warn-about-selected-sibling-claim-boundaries separately from these rejection criteria.
