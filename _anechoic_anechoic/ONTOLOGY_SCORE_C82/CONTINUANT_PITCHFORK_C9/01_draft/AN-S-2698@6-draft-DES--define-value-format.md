---
atom_family: SPEC
atom_id: AN-S-2698
container:
  component: C9
tier: 1
context:
  lens: DES
state:
  status: draft
  version: 6
  updated_at: 2026-11-05 19:33:47 +0400
---
## Summary

Define Value Format

## Claim

### Prose Claim

Square brackets enclose a Format and any conditions. After a Property they restrict its direct-value domain: `[int]` selects the integer Format and `[int, 0..100]` restricts it to that inclusive range. In `p.*[name format]` and `p.**[name format]`, the Format constrains selected immediate and recursive dependent Property names, respectively; those name counts remain separate from direct-value counts. Multiple conditions apply together as AND; parentheses specify the grouping of mixed conditions. A Model kind referenced through `<Kind>` can supply an object Format, and OR can combine Model-kind domains under the separate Model-kind Format rule. A Format constrains each direct Property value separately from Property occurrence and value cardinality; it does not create an instance or turn a literal into a Node.

Data Type names a value domain. Uniqueness Selection names the comparison population. List and map are Carrier structures, not Value Formats. A YAML sequence carries multiple values, and a mapping carries dependent Properties. `ref` is not a Value Format. Identifying values use the `string` Format; their Definition identifies the referenced object. Nested Properties have independent Formats and cardinalities. YAML null and an empty string each count as one direct value when present; Format and applicable conditions determine admissibility.

In `p{::occ} :: [<Kind>]{::valuecount}`, the bounds count Property occurrences and direct values respectively, not every instance of Kind in the Project.

## Semantics

A Format describes the admissible values. Markdown is a value Format for Markdown content; a Format does not impose uniqueness.
