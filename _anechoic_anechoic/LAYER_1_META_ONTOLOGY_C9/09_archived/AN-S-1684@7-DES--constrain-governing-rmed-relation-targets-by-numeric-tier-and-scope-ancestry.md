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
  version: 7
  updated_at: 2026-10-25 17:32:27 +0400
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
  ordering: same_scope_lower_target_tier_or_strict_ancestor_or_project_configuration_core_prerequisite
```

## Semantics

Ordering contexts follow CA-D-637. A verified Project Goal uses its Target Project, while its owner remains the Operator Actor; ordinary endpoints use their Local Scope Unit. The numeric comparison and strict-ancestor rule are unchanged. The exact Project Configuration → Core Meta-Model prerequisite alternative is the logical-role declaration in CA-R-1218; it does not authorize the reverse, another source-role pair, a transitive edge, or a relation from a containing Project or Methodology Sources Scope Unit.
