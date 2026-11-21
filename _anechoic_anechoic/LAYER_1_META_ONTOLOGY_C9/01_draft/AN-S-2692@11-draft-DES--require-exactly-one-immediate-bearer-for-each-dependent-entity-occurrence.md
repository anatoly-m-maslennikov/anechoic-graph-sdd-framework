---
atom_family: SPEC
atom_id: AN-S-2692
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: draft
  version: 11
  updated_at: 2026-10-28 19:24:50 +0400
---
## Summary

Require exactly one immediate bearer for each dependent Entity occurrence

## Claim

### Prose Claim

```yaml
graph_rule_type: cardinality
applies_to:
  node: Subject/ANECHOIC/Graph/Node/Project Model/Selection//Dependent Entity Occurrences
  relation_type: IS_BORNE_BY
  direction: outgoing
condition:
  other_endpoint:
  - Subject/ANECHOIC/Graph/Node
  minimum: 1
  maximum: 1
```

## Details

Superseded preparation: CA-A-1242 removes the special Graph Rule branch and Atom Type. Do not promote this legacy Graph Rule packet entry as written. Preserve its useful formal constraints/schema evidence for incorporation into the appropriate Definition Claims; no Current rule or predecessor is deleted by this marker.
