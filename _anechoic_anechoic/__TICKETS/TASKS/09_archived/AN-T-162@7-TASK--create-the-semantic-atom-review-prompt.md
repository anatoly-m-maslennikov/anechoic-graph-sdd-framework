---
atom_family: TKT
atom_id: AN-T-162
container:
  component: C00
priority: 2
context:
  template: task
state:
  status: archived
  version: 7
  updated_at: 2026-10-24 13:13:51 +0400
---
## Summary

Create the semantic Atom review prompt

# Summary

Create the semantic Atom review prompt

## Claim

the AI Agent **must** deliver a tested review prompt that evaluates one source Atom with sufficient governing context for Claim atomicity, internal consistency, CCE conformance, correct Content Role, **and** alignment with Project Principles.

## Definition of Done

the Plan is **not** Done **if** an agreed semantic criterion is omitted, **or** required context is silently missing, **or** fixtures fail **to** distinguish valid composite Claims from independent Claims, **or** findings lack evidence **and** authority, **or** the prompt treats a review recommendation as approval **to** mutate sources.

## Details

- place the reusable prompt implementation under the declared prompt-owning Scope Unit; reuse relevant current authoring **and** review authority.
- inputs include the complete Atom Carrier, applicable methodology, Project Principles, target Scope Unit context, **and** relevant related Atoms; missing context produces an explicit incomplete review.
- check **=1** independently replaceable Claim, including valid composite Claims; distinguish Claim Target Scope Unit from textual Claim restrictions **and** verify role-specific target admission.
- check consistency between frontmatter **and** named body Properties; faithful Summary; correct Content Role/Type; valid Subjects **and** direct Relations; no duplicated authority, unresolved contradictions, **or** missing prerequisites.
- apply the full current CCE profile, including Operators, Term spelling/case, Scope Unit names, sentence case, mathematical cardinality, simple wording, structured points, **and** understandable Claim expression.
- produce findings with exact evidence, applicable authority, confidence, proposed disposition, **and** uncertainty. separate review from approved repair.
- test with valid **and** invalid examples, including multiple independent Claims, legitimate composite Claims, mismatched metadata/body, inappropriate Content Role, CCE violations, **and** principle conflicts.
- apply current source authority, including CA-R-1598 **and** CA-D-478–483; do **not** treat an outdated compiled copy as newer authority.
- check Project Principles **before** escalating uncertainty; ask the Operator **if** confidence remains **<99%**. do **not** silently weaken an Evaluation **or** discard a finding **to** pass.
- preserve unrelated work **and** history; follow the current revision, replacement, Summary identity, **and** approval rules.
