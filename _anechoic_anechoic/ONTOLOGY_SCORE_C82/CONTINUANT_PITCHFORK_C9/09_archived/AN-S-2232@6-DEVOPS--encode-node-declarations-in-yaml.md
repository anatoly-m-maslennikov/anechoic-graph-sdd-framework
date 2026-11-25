---
atom_family: SPEC
atom_id: AN-S-2232
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 6
  updated_at: 2026-11-09 00:03:55 +0400
---
## Summary

Encode Node Declarations in YAML

## Claim

### Prose Claim

Deliver a Node Declaration’s Header through the common recursive Atom-to-YAML mapping. Preserve its declared Property hierarchy and value cardinalities. Header names and named values use the common lowercase-and-underscore encoding.

The declared Main Subject identifies the canonical HAS_ACTIVE_SUBJECT target. Direct Relation facts have one authored source; their encoded names retain that Relation’s meaning. Container references retain the declared target kind and exact target ID.

### Formal Claim

```CFEL
# instances
$declaration[<Atom>, (.Header.Context.Role = Requirement) AND (.Header.Context.Form = Declaration)] >> $carrier[<Carrier>];

$declaration.Header >> $carrier.frontmatter
```

## Details

Named-value encoding examples: `Requirement` becomes `requirement`; `Declaration` becomes `declaration`. IDs retain their exact spelling.
