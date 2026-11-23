---
atom_family: SPEC
atom_id: AN-S-1756
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: archived
  version: 28
  updated_at: 2026-10-25 17:32:27 +0400
---
## Summary

Serialize External Project Goal Filenames

# Summary

Serialize External Project Goal Filenames

## Scope

external Project Goal filenames.

## Claim

**every** external Project Goal filename **must** begin with the unqualified canonical Atom ID prefix `<CANONICAL_ATOM_ID>-` for a Current Project Goal or the once-qualified canonical Atom ID prefix `<CANONICAL_ATOM_ID>@<VERSION>-` for an Archived Project Goal, followed by `<OPERATOR_NAMES>-DEFINES_GOAL_FOR-<PROJECT_SCOPE>--<SUMMARY_SLUG>.<EXT>`.

The `<OPERATOR_NAMES>` filename token **must** identify the registered Operator; `<PROJECT_SCOPE>` **must** preserve the exact registered Project Name. The canonical current ID or once-qualified archived ID is the identity prefix; no additional Project prefix, Content Role letter or unrelated number may be inserted into the preserved segment.

## Details
