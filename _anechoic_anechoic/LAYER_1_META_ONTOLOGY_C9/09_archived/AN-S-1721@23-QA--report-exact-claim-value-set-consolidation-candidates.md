---
atom_family: SPEC
atom_id: AN-S-1721
container:
  component: C9
tier: 4
context:
  lens: QA
state:
  status: archived
  version: 23
  updated_at: 2026-10-24 12:35:51 +0400
---
## Summary

Report Exact Claim Value-Set Consolidation Candidates

# Summary

Report Exact Claim Value-Set Consolidation Candidates

## Scope

Claim Value Set consolidation candidates.

## Claim

the Evaluation **must** report **`=1`** Claim Value Set consolidation candidate **only** **if** **every** contributing active Atom has the same Atom Scope, Atom Governed Subject, Claim Target Scope Unit, textual Claim Scope, Property, **and** exact qualifiers, has **`=1`** mechanically parseable single-value Claim, **and** differs **only** by **`=1`** unique value proven through IS_ALLOWED_VALUE_OF for that Property; it **must not** mutate, merge, archive, replace, compile, **or** change a Source Atom by another operation, use semantic **or** LLM inference, **or** cause Applicable Methodology compilation **to** fail.

## Details
