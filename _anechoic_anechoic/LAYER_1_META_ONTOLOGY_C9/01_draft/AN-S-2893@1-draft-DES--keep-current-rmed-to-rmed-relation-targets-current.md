---
atom_family: SPEC
atom_id: AN-S-2893
container:
  component: C9
tier: 9
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-10-22T01:39:08+04:00'
---
# Summary

Keep Current RMED-to-RMED relation targets Current

```yaml
graph_rule_type: endpoint_constraint
applies_to:
  relation: direct
  source:
    lifecycle_group: Current
    content_role:
      - Requirement
      - Method
      - Evaluation
      - Delivery
  target:
    content_role:
      - Requirement
      - Method
      - Evaluation
      - Delivery
condition:
  target_lifecycle_group: Current
  on_unresolved_endpoint_lifecycle: unresolved
```

## Details

The `endpoint_constraint` mapping is proposed only. [CA-D-637@5](../../07_delivery/CA-D-637-CORE_META_MODEL-CORE--carry-a-formal-graph-rule-as-yaml-with-a-readable-summary.md) does not yet admit an endpoint-constraint schema.

Source: [CA-R-1676@21](../CA-R-1676-CORE_META_MODEL-CORE-REQUIREMENT--keep-rmed-to-rmed-relations-within-active-authority.md). Current is a lifecycle group, not an Atom.Status value: exclude Draft and archived sources; include non-archived Done/Canceled where their role permits those statuses. Use authoritative lifecycle/placement, not historical Status bytes alone. Apply only to direct relations whose source and target roles are both in RMED. Relations involving Operations or other kinds are outside this rule, not implicitly prohibited.

The proposed unresolved-lifecycle outcome covers both endpoints, including source applicability. If either role-qualified endpoint's lifecycle cannot be determined, report unresolved before treating the source as out of scope or the target as conforming. Unknown membership is not a passing or automatically inapplicable case.
