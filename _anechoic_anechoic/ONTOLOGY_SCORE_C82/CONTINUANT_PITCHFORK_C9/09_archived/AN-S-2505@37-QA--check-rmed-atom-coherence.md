---
atom_family: SPEC
atom_id: AN-S-2505
container:
  component: C9
tier: 5
context:
  lens: QA
state:
  status: "archived"
  version: 37
  updated_at: "2026-11-25T22:00:01.884953+00:00"
---
## Summary

Check RMED Atom coherence

## Claim scope

Local review of an individual complete RMED Atom against its carried text and applicable rules.

## Claim

### Prose Claim

A complete RMED Atom passes this local Evaluation only when it has one source-faithful Summary under # Summary, exactly one content.claim under ## Claim, and optional Claim scope, Semantics and Details in the registered order. Its one Type-defined Claim contains prose, an optional formal_claim child, or both; they must agree rather than supply unrelated or contradictory contributions. Assess the independently replaceable contribution, applicable boundary, support and Summary from that one Claim.

## Details

Check Properties against CA-D-479 and the applicable Type. Do not fail absent optional sections; fail an omitted Claim scope only when the full-applicability omission condition is not met. For a formal part parse its declared expression under the applicable Definition and Graph Syntax, check its admitted fields/schema and absence of a duplicate frontmatter Claim. Do not infer a defined schema, fulfilled rule, actual run or semantic correctness merely from parsing.

Review prose against the applicable writing rules. Review formal content against its declared syntax. Semantics explains meaning, Details supports the Claim, and neither supplies another normative Claim. Report concrete local source evidence for findings and retain unresolved evidence as gaps. This remains the atom_local profile: it does not silently add model-wide conflict, Subject completeness, target existence, Tier hierarchy or Principle audits. Existing Operator authority remains applicable. A local pass is not whole-methodology conformance.

R-only scope refinement (CA-A-1244): the optional ### Formal claim / content.claim.formal_claim is admitted only for Requirement Atoms for now. Method, Evaluation and Delivery have prose Claims with no operative formal child; code examples remain examples. Any earlier generic optional-formal wording in this Draft is limited by that Role condition. The complete one-Claim contract and optional supporting sections remain unchanged.
