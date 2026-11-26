---
atom_family: SPEC
atom_id: AN-S-1786
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: "archived"
  version: 16
  updated_at: "2026-11-25T20:25:07.493321+00:00"
---
## Summary

Serialize numbered version-qualified Draft Atom filenames

## Claim

### Prose Claim

A Draft revision of an existing Atom carries its exact base canonical ID and positive integer proposed Version at their declared Header paths. The logical Status is Draft, encoded as `draft` by the common YAML rule. Its filename carries exactly one `<canonical-ID>@<proposed-version>-draft` marker as the Atom-ID segment before the remaining mutable filename components.

For an existing Atom, `<proposed-version>` follows the applicable current revision rule, normally `<current-version> + 1`. The filename marker qualifies the proposed revision; it is not a second Header identity.

A new Atom Draft allocates an unused canonical ID, carries logical Draft Status and integer Version 1 at their declared Header paths, and uses the same qualified filename marker with `@1-draft`. Classification-only changes and other non-replacement edits keep the ordinary identity rule; this filename contract adds no new identity meaning.

Existing legacy Draft filenames are not normalized, renamed, or migrated automatically by this rule.
