---
atom_family: SPEC
atom_id: AN-S-2770
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 28
  updated_at: 2026-11-02 00:18:22 +0400
---
## Summary

Serialize Atom Subjects in Frontmatter

## Claim

### Prose Claim


New or migrated Markdown Atom carriers.


For Markdown Atom carriers, encode `subjects` as a mapping with one scalar nonempty Entity path under `active` and zero or more unique nonempty Entity paths as a YAML sequence under `passive`. An omitted `passive` means zero. The grouping mapping has no direct value; its child values are counted separately. A Draft may be incomplete before promotion.

Preserve the decoded Entity paths exactly under the applicable notation and resolve targets under the applicable Subject rules. A defining Atom may introduce its target and path together. Do not add an intermediate reference object or a repeated target-type field. YAML quotes are not part of the decoded expression; preserve escapes and reference boundaries. Each YAML key occurs once within its own mapping. Preserve formal cardinality annotations and decoded Entity escapes exactly; do not serialize notation as extra YAML fields.

The canonical keys are `active` and `passive`. Existing `governs` and `depends_on` remain readable during carrier migration. Mixed old and new aliases with unequal values are invalid. Equal aliases can be read during transition, without asserting additional Subjects.

## Details

Reference migration preserves target identity and follows the governing Entity rules. Subject paths are distinct from formal Relation expressions in the body Claim.
