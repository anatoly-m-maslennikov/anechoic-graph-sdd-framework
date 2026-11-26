---
atom_family: SPEC
atom_id: AN-S-2802
container:
  component: C9
tier: 3
context:
  lens: DES
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-25T22:35:56.055171+00:00"
---

## Summary

Specify Python declaration support

## Claim

### Prose Claim

- Use ordinary Python types, literals, comparisons, comprehensions, and standard-library functions in Claims.
- Use standard-library dataclasses for typed declaration records. Use an integer for an exact cardinality. Use `Cardinality(minimum=..., maximum=...)` for an inclusive range, with `None` for an unbounded maximum.
- Carry dependent Property names, traversal depth, and Relation endpoints as typed declaration data.
- Declare immediate sibling order with `ordered_dependent_property_pairs`. Each pair names the Property ordered immediately before the second. Apply the pair within the bearer and Role scope of the declaration.
- Statically resolve declaration functions, class imports, Model addresses, and Relation names. Resolve callbacks separately from declaration loading. Use typed Engine data when evaluating reviewed callbacks.
- Declare singleton populations as exactly one instance within the Project. Apply this to the Project and its root Project Package.
- Preserve the full qualified Topic address and the one Main Subject per Atom.

- Apply dependent Property constraints to immediate children by default. An explicit recursive selector covers descendants at every depth and preserves the original declaring Atom.
- Resolve omitted Property occurrence constraints from the effective Model. Keep field presence, direct value cardinality, and dependent Property cardinality distinct.
- Within the applicable Declaration and its inherited rules, admitted literal values are alternatives. A value satisfies at least one admitted alternative when the domain names any. It also satisfies every applicable format and cardinality constraint.
- Preserve both a direct Markdown value and declared dependent Properties when a field has both. Bind only declared headings as Properties.
