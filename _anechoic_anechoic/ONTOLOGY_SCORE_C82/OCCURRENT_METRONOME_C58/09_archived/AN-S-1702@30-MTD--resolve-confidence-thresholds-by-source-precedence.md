---
atom_family: SPEC
atom_id: AN-S-1702
container:
  component: C58
tier: 3
context:
  lens: DOM/MTD
state:
  status: "archived"
  version: 30
  updated_at: "2026-11-25T23:05:43.699147+00:00"
---
## Summary
Resolve confidence thresholds by source precedence

## Claim

### Prose Claim

For a governed autonomous decision, use the first applicable source:

1. The Operator’s input for this decision.
2. An explicit threshold declared for the work.
3. The nearest declared enclosing override.
4. The applicable configuration default.

Read only sources that the applicable methodology admits. A threshold is an integer from 0 to 100. If the reached source is missing, invalid, or ambiguous and no applicable value resolves, ask the Operator before proceeding. Continue autonomously only at or above the threshold and within existing authority.

Use current sources. Preserve an absent override and each explicit selection. Legacy Plan carriers and Framework Settings keep their existing field names and precedence for compatibility.
