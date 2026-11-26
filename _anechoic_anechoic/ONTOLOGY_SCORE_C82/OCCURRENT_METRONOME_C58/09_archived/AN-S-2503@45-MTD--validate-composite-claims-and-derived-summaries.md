---
atom_family: SPEC
atom_id: AN-S-2503
container:
  component: C58
tier: 3
context:
  lens: DOM/MTD
state:
  status: "archived"
  version: 45
  updated_at: "2026-11-25T21:42:16.100243+00:00"
---
## Summary

Validate Composite Claims and Derived Summaries

## Claim

### Prose Claim


the Claim boundary, applicability, supporting Details, **and** Summary of an Atom.


For a native Atom, check the declared Template and its applicable sections. Check that supporting Details stay within the primary contribution and that the Summary preserves its applicability under AN-S-2574. Apply the following Claim and Scope layout tests only to legacy RMED:

- the Atom has **`!=1`** Claims, **`!=1`** resolved Claim Target Scope Units, an independently replaceable component inside **`=1`** Claim, ambiguous composite grouping, **or** a non-deterministic Scope Expression.
- RMED Scope is missing its applicability description, merely repeats the carried current **or** target Scope Unit, introduces a second independently replaceable Claim, **or** conflicts with the Claim. applicability **must** be explicit **in** Scope rather than maintained independently **in** Claim **or** Details.
- Details change, contradict, broaden, narrow, **or** add an independent contribution **to** the primary contribution within its applicability instead of expanding it under CA-R-2503-CORE_META_MODEL-DEFINITION--keep-details-within-the-primary-contribution.
- Summary is **not** source-faithful **to** the finalized primary contribution under AN-S-2196 **and** CA-R-1273-CORE_META_MODEL-CORE-REQUIREMENT--keep-summary-source-faithful, including its applicability restrictions. for RMED, use the Claim read within Scope; a Summary of Scope alone fails. a Summary sourced from Analysis Results **or** TLDR instead of Question fails this check.

evaluate restrictions **to** selected sibling Scope Units under AN-S-1729 separately from these rejection criteria.
