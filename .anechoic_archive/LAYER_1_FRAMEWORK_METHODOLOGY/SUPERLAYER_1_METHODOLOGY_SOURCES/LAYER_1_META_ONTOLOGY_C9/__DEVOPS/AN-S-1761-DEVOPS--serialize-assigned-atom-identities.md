---
atom_family: SPEC
atom_id: AN-S-1761
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: active
  version: 31
  updated_at: 2026-11-09 00:51:00 +0400
---
## Summary

Serialize Assigned Atom Identities

## Claim

### Prose Claim

Every assigned Current or Archived Atom ID must begin with the registered uppercase Project identity prefix and match `<PROJECT_PREFIX>-<CONTENT_ROLE_LETTER>-<GLOBAL_NUMBER_WITHIN_CONTENT_ROLE>`. The Content Role Identity Letter is one of `C`, `A`, `P`, `R`, `M`, `E`, `D`, or `O`.

Every Draft carries its exact base canonical ID and positive integer Version at their declared Header paths. The logical Status is Draft, encoded as `draft` by the common YAML rule. Its filename carries exactly one `<canonical-ID>@<version>-draft` marker before the remaining mutable filename components.

For a Draft revision of an existing Atom, `<version>` follows the applicable current-version-plus-one rule. A new Atom Draft allocates an unused canonical ID and uses integer Version 1 at its declared Header path with the same qualified `@1-draft` filename marker. Classification-only changes and other non-replacement edits retain the ordinary identity rule; this Draft marker does not add a new identity meaning.

Existing legacy Draft filenames are not normalized, renamed, or migrated automatically by this rule.
