---
identity:
  atom_id: AN-S-1721
context:
  container:
    component: C00
  tier: 4
  lens: QA
state:
  status: draft
  version: 36
  updated_at: 2026-11-02 08:06:47 +0400
---
## Summary

Report Exact Claim Value-Set Consolidation Candidates

## Claim

### Prose Claim


Claim Value Set consolidation candidates.


the Evaluation **must** report **`=1`** Claim Value Set consolidation candidate **only** **if** **every** contributing active Atom has the same Atom Scope, Atom Governed Subject, Claim Target Scope Unit, textual Claim Scope, Property, **and** exact qualifiers, has **`=1`** mechanically parseable single-value Claim, **and** differs **only** by **`=1`** unique value proven as allowed by the `:` qualification for that Property; it **must not** mutate, merge, archive, replace, compile, **or** change a Source Atom by another operation, use semantic **or** LLM inference, **or** cause Applicable Methodology compilation **to** fail.
