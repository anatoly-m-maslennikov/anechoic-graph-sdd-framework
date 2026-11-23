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
  version: 24
  updated_at: 2026-10-27 19:59:23 +0400
---
## Summary

Serialize Atom Subjects in Frontmatter

# Summary

Serialize Atom Subjects in Frontmatter

## Scope

New **or** migrated Markdown Atom Carriers.

## Claim

a new **or** migrated Markdown Atom Carrier **may** omit `subjects` when it has no Subject Relations. **when** present, `subjects.governs` **may** contain one scalar Subject Path **and** `subjects.depends_on` an unordered collection of **`>=0`** unique scalar Subject Paths; an absent `governs` key **means** zero governed Subjects **and** an absent dependency collection **means** zero dependencies. the `governs` **or** `depends_on` key encodes the Subject Relation Kind; the source Atom is implicit **and** the scalar value encodes its target's Subject Path, **not** the Subject Relation itself. these values resolve their canonical targets under CA-R-1202-CORE_META_MODEL-RULE--resolve-every-direct-subject-target-once **without** an intermediate Subject/Entity **or** Subject/Reference field **or** a repeated target-kind field.

## Details

an existing unmigrated Carrier **may** temporarily retain `subjects.<governs|depends_on>.<continuant|occurrent>` **only** **until** its explicitly assigned carrier-migration Task is executed. this compatibility is migration-limited, preserves the same direct relation facts **and** target identities, **and** does **not** establish a second canonical representation. legacy temporal-classification authority **and** bulk Carrier conversion require their separately assigned migration Tasks.
