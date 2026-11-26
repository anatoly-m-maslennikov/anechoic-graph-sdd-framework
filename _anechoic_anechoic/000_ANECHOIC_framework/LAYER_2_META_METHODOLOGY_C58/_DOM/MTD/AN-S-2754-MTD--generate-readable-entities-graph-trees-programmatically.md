---
atom_family: SPEC
atom_id: AN-S-2754
container:
  component: C58
tier: 4
context:
  lens: DOM/MTD
state:
  status: "active"
  version: 27
  updated_at: "2026-11-25T22:46:50.244972+00:00"
---
## Summary

Generate readable Entities Graph trees programmatically

## Claim

Select the exact source frontier and the requested display from the available Model or Entity views. Record the source selection and each contributing source revision. Report unreadable inputs, unresolved relations, and unknown facts.

Render the selected hierarchy and its Property details from declared facts. Preserve the distinction between specialization, instance membership, containment, Properties, and allowed values. Keep source-defined sibling order where it exists. Otherwise sort by readable name and qualified identity.

Make the primary entity tree and Property detail views independently readable. Use declared Relation names and directions in the named Relation view. When showing effective rules, distinguish declared, inherited, and overriding rules and identify their source Manifests. When saving the result, use the Markdown Projection format declared by AN-S-275.
