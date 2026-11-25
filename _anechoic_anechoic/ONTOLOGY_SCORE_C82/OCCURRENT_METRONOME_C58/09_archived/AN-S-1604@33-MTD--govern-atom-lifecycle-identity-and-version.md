---
atom_family: SPEC
atom_id: AN-S-1604
container:
  component: C58
tier: 2
context:
  lens: DOM/MTD
state:
  status: "archived"
  version: 33
  updated_at: "2026-11-25T19:35:28.604568+00:00"
---
## Summary

Govern Atom lifecycle identity and Version

## Claim

### Prose Claim

Initialize Updated At when creating an Atom revision. On every in-place edit, set Updated At to the edit time and retain the Atom ID and Version. This includes changes to Status during promotion or archival. A file-only move preserves Updated At. Archival preserves unrelated content and uses the archived Status and version-qualified reference.

Creating a Draft for a new Version of an existing Atom assigns Version N+1 once. Promotion retains that Version when Summary and Content Role are unchanged. A changed Summary or Content Role instead requires a fresh Atom ID and Version 1 at promotion. Lossless serialization that preserves the Summary value is not a Summary change.

A Current Atom update composes creation of a new Draft, archival of its Current predecessor, and promotion of the Draft. Capture the predecessor's Current Status once and use that same Status for promotion. A new Atom is assigned its own ID and initial Version. Preserve a descendant's Updated At when an ancestor move leaves that descendant's Header and Content unchanged.
