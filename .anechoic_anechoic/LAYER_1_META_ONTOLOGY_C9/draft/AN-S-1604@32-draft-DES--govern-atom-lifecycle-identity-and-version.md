---
identity:
  atom_id: AN-S-1604
context:
  container:
    component: C9
  tier: 2
  lens: DES
state:
  status: draft
  version: 32
  updated_at: '2026-11-13T08:50:40.274667+00:00'
---
## Summary

Govern Atom lifecycle identity and Version

## Claim

### Prose Claim

Draft edits and directly authorized in-place edits preserve the Atom's ID, Version, and Updated At. A Status-only change or archival preserves Version and Updated At; archival preserves the predecessor's unrelated content and uses the Archived Status and version-qualified identity.

Creating a Draft for a new Version of an existing Atom assigns an unused Version and initializes its creation timestamp. For an Atom ID with no published Version, promoting its Version 1 Draft publishes Version 1 and preserves any other Drafts for that ID. When promotion updates an existing Atom under the same ID, the promoted Version is one greater than the maximum existing Version for that ID in the Project, including the selected Draft. A changed Summary or Content Role requires a fresh Atom ID and Version 1 at promotion. Lossless serialization that preserves the Summary value is not a Summary change.

A Current Atom update composes creation of a new Draft, archival of its Current predecessor, and promotion of the Draft. Capture the predecessor's Current Status once and use that same Status for promotion. A new Atom is assigned its own ID and initial Version. Moving an ancestor without changing a descendant's own bytes, metadata, direct owner, or placement relative to that owner does not edit that descendant.
