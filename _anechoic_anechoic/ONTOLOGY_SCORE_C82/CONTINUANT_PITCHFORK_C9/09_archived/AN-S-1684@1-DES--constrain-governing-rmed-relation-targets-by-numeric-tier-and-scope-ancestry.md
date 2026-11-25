---
atom_family: SPEC
atom_id: AN-S-1684
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-23 23:13:47 +0400
---
## Summary

Constrain Governing RMED Relation Targets by Numeric Tier and Scope Ancestry

# Summary

Constrain Governing RMED Relation Targets by Numeric Tier and Scope Ancestry

```yaml
graph_rule_type: endpoint_constraint
applies_to:
  relation_selection: "Subject/Domain/Node/Continuant/Selection//Stored Governing RMED Relation Occurrences"
condition:
  ordering: same_scope_lower_target_tier_or_strict_ancestor
```

