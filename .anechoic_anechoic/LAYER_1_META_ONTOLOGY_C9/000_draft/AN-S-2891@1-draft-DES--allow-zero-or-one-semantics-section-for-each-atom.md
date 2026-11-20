---
atom_family: SPEC
atom_id: AN-S-2891
structure:
  container:
    component: C9
context:
  lens: DES
state:
  status: draft
  version: 1
  updated_at: '2026-10-22T01:39:08+04:00'
---
# Summary

Allow zero or one Semantics section for each Atom.

```yaml
graph_rule_type: cardinality
applies_to:
  node: "Entity/Node/Continuant/Atom"
  property: "Entity/Node/Continuant/Atom.Semantics"
condition:
  minimum: 0
  maximum: 1
```

## Details

Provenance: `../CA-R-1946-CORE_META_MODEL-GENERAL--define-atom-semantics.md` defines Semantics as Atom content without requiring it on every Atom; `../../07_delivery/CA-D-637-CORE_META_MODEL-CORE--carry-a-formal-graph-rule-as-yaml-with-a-readable-summary.md` permits an optional Semantics section for formal Graph Rules. The operative block is a proposed property-cardinality schema only; current CA-D-637 admits cardinality only for relations. It creates no parser, validator, resolver, evaluator, or activation.
