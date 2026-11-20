---
identity:
  atom_id: AN-S-2892
context:
  container:
    component: C9
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-10-22T01:39:08+04:00'
---
# Summary

Constrain the endpoint kinds of evaluation_for

```yaml
graph_rule_type: whitelist
applies_to:
  relation_type: evaluation_for
condition:
  source:
    - "Entity/Node/Continuant/Atom/Content Role: Evaluation"
  target:
    - "Entity/Node/Continuant/Atom/Content Role: Requirement"
    - "Entity/Node/Continuant/Atom/Content Role: Method"
    - "Entity/Node/Continuant/Atom/Content Role: Evaluation"
    - "Entity/Node/Continuant/Atom/Content Role: Delivery"
    - "Entity/Node/Continuant/Atom/Content Role: Operations"
```

## Details

Source: [CA-R-1018@22](../CA-R-1018-CORE_META_MODEL-CORE--register-evaluation-targets.md). The whitelist checks only endpoint kinds; it does not require a connection or establish that a supplied target's authority is actually checked. The relation's meaning and other constraints remain separate.

This Draft uses the existing Whitelist shape from [CA-D-637@5](../../07_delivery/CA-D-637-CORE_META_MODEL-CORE--carry-a-formal-graph-rule-as-yaml-with-a-readable-summary.md). Draft creation does not activate this rule or establish runtime evaluation.
