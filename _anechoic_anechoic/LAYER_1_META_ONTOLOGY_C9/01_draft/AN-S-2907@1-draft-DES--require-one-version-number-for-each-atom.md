---
atom_family: SPEC
atom_id: AN-S-2907
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

Require one Version Number for each Atom.

```yaml
graph_rule_type: cardinality
applies_to:
  node: "Entity/Node/Continuant/Atom"
  property: "Entity/Node/Continuant/Atom.Version Number"
condition:
  minimum: 1
  maximum: 1
```

## Details

Provenance: `../CA-R-1415-CORE_META_MODEL-GENERAL--give-every-atom-revision-one-version.md` requires one positive integer Version. The operative block is a proposed property-cardinality schema only: current `../../07_delivery/CA-D-637-CORE_META_MODEL-CORE--carry-a-formal-graph-rule-as-yaml-with-a-readable-summary.md` admits cardinality only for relations. It creates no parser, validator, resolver, evaluator, or activation.
