---
atom_family: SPEC
atom_id: AN-S-4051
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 1
  updated_at: 2026-10-29 14:16:32 +0400
---
## Summary

Define Atom Tier Label

## Claim

Tier Label is an optional readable name for an Atom's numeric Tier. It does not replace the integer Tier, create a second rank, or mean the Atom's separate Label property. When present for Tier 0, 1, 2, 3 or 4, it is respectively Principle, Core, General, Standard or Detail. Every Tier may omit its Label; numeric Tiers 5 and higher remain valid without a predefined Label. Other Tier values retain their existing admission rules.

### Formal claim

```text
Atom.Tier.Label[string]{0..1}
Atom.Tier.Label: Principle
Atom.Tier.Label: Core
Atom.Tier.Label: General
Atom.Tier.Label: Standard
Atom.Tier.Label: Detail
```

## Semantics

The mapping names graph-ordering levels; it does not add semantic precedence, importance or conflict-resolution authority. The listed names are not a closed set of numeric Tiers.
