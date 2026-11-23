---
atom_family: SPEC
atom_id: AN-S-1752
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 18
  updated_at: 2026-10-23 03:06:32 +0400
---
## Summary

Serialize Atom Revision Metadata **in** Frontmatter

# Summary

Serialize Atom Revision Metadata **in** Frontmatter

## Scope

Markdown Atom Revision Carriers.

## Claim

**every** Markdown Atom Revision Carrier **must** serialize its positive integer Version as `version` **and** its Project-time Updated At value as `updated_at` **in** YAML frontmatter.

## Details

- `version` is a YAML integer **>=1**, **not** a Boolean **or** numeric string.
- `updated_at` is a quoted YAML string containing **=1** valid date, time **and** explicit UTC offset. accept the existing `YYYY-MM-DD HH:MM:SS +HHMM` form **and** the equivalent ISO 8601 `YYYY-MM-DDTHH:MM:SSZ` **or** `YYYY-MM-DDTHH:MM:SS+HH:MM` form, including optional fractional seconds. offset signs **may** be positive **or** negative; reject a missing timezone, impossible date, **or** invalid offset.
- lexical differences representing the same instant do **not** alone change Revision identity. this Delivery serializes Updated At; it does not classify whether an edit changes governed meaning.
