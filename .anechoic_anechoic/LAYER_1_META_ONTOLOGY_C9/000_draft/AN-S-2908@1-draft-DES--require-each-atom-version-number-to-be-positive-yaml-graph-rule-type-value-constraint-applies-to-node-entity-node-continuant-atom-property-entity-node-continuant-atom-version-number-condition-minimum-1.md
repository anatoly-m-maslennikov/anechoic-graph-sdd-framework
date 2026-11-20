---
identity:
  atom_id: AN-S-2908
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

Require each Atom Version Number to be positive.

```yaml
graph_rule_type: value_constraint
applies_to:
  node: "Entity/Node/Continuant/Atom"
  property: "Entity/Node/Continuant/Atom.Version Number"
condition:
  minimum: 1
```

## Details

Provenance: `../CA-R-1415-CORE_META_MODEL-GENERAL--give-every-atom-revision-one-version.md` requires a positive integer Version. The operative block is a proposed value-constraint range schema only: `../../07_delivery/CA-D-637-CORE_META_MODEL-CORE--carry-a-formal-graph-rule-as-yaml-with-a-readable-summary.md` does not yet admit value constraints. It creates no parser, validator, resolver, evaluator, or activation.
