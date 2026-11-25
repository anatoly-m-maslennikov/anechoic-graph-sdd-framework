---
atom_family: SPEC
atom_id: AN-S-3550
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: archived
  version: 29
  updated_at: 2026-10-30 17:10:32 +0400
---
## Summary

Define Atom Subjects

## Claim scope

the Atom Subjects Property.

## Claim

Subjects is the structured Atom property that links the Atom to its governed Subject and contextual dependencies. A complete Current Atom has exactly one direct GOVERNS target and zero or more direct DEPENDS_ON targets. The grouping has no direct scalar value; each child is counted independently. Drafts can remain incomplete until promotion.

The links preserve their target identities without copying the target or creating a separate Subject object for each link. A governing Atom may introduce its governed target; that target need not pre-exist as a separate artifact.

### Formal claim

```text
Atom.Subjects{0}
Atom.Subjects.Governs[string]{1}
Atom.Subjects.Depends On[string]{0+}
```
