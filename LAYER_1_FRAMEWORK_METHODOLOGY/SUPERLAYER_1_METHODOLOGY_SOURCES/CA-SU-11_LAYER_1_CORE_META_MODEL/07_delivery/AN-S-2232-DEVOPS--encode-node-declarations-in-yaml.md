---
atom_family: SPEC
atom_id: AN-S-2232
structure:
  container:
    component: C9
  tier: 3
context:
  lens: DevOps
state:
  status: active
  version: 7
  updated_at: '2026-11-13T05:43:10.850606+00:00'
---
## Summary

Encode Node Declarations in YAML

## Claim

### Prose Claim

Deliver the selected Node Declaration as a whole to the selected Carrier. Deliver its Header to the Carrier frontmatter through the common recursive Atom-to-YAML mapping. Preserve its declared Property hierarchy and value cardinalities. Header names and named values use the common lowercase-and-underscore encoding.

The declared Main Subject identifies the canonical HAS_ACTIVE_SUBJECT target. Direct Relation facts have one authored source; their encoded names retain that Relation’s meaning. Container references retain the declared target kind and exact target ID.

### Formal Claim

```python
# instances
deliver(
    source="$declaration[<Atom>, (.Header.Context.Role = Requirement) AND (.Header.Context.Form = Declaration)]",
    carrier="$carrier[<Carrier>]",
)
```

## Details

Named-value encoding examples: `Requirement` becomes `requirement`; `Declaration` becomes `declaration`. IDs retain their exact spelling.
