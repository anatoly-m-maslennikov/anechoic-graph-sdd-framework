---
atom_family: SPEC
atom_id: AN-S-2794
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DES
state:
  status: active
  version: 2
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Require unique Property tuples

## Claim

### Prose Claim

Require distinct value tuples across the selected Project instances. An optional condition restricts the population.

- Use each selected instance's state in one explicit Project snapshot. Use one state per selected logical instance. Without a condition, evaluate the complete selected population regardless of Status Group or containment, including selected Drafts and Archived instances. An incomplete or unresolved population is an error. A known empty population satisfies uniqueness.
- Evaluate a condition on each candidate instance before resolving tuple Properties. Relative Properties bind to that same instance. False excludes it; unresolved, invalid or ambiguous conditions are errors. Use Python Boolean expressions.
- For each selected instance, bind every tuple Property to that same instance. Each must have exactly one valid scalar value; missing, invalid or multiple values fail the constraint.
- Two distinct selected logical instances must not have equal value tuples. Repeated references or Carrier representations of the same logical instance do not create additional instances. Do not infer that two instances are one merely because their key tuples match.
- Compare scalar values in their declared Format without implicit normalization or coercion. A declared reference compares by its resolved target identity; an absent or ambiguous binding is an error, with no raw Carrier-locator fallback. Tuple components need not be individually unique.
- Optional Properties require an explicitly resolved subset whose members carry the required values; do not silently skip missing rows.

Declare the tuple keys and any population restriction with the Python Model.
