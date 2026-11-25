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
  version: 36
  updated_at: "2026-11-25T20:43:05.178939+00:00"
---
## Summary

Govern Atom lifecycle identity and Version

## Claim

### Prose Claim

Initialize Updated At when creating an Atom revision. On every in-place edit, set Updated At to the edit time and retain the Atom ID and Version. This includes changes to Status during promotion or archival. A file-only move preserves Updated At. Archival preserves unrelated content and uses the archived Status and version-qualified reference.

Bind an edit Draft to the selected Current revision. Assign one more than the greatest occupied Version for that Atom ID. A no-op retains its Version and Updated At. Draft identity and promotion depend on the selected source and admitted fields. A retained Draft history or Journal entry is optional. Promotion retains that Version when Summary and Content Role are unchanged. A changed Summary or Content Role instead requires a fresh Atom ID and Version 1 at promotion. Lossless serialization that preserves the Summary value is not a Summary change.

A Current Atom update composes creation of a new Draft, archival of its Current predecessor, and promotion of the Draft. Capture the predecessor's Current Status once and use that same Status for promotion. A new Atom is assigned its own ID and initial Version. Preserve a descendant's Updated At when an ancestor move leaves that descendant's Header and Content unchanged.

## Status transitions

A finalized Spec Draft becomes Ready. It becomes Active when implementation starts and Archived when retired.

A Ticket moves from Draft to Backlog, then to In Queue. Work in progress keeps Status In Queue. Planning Tasks finish Done or Canceled. Issues finish Resolved or Canceled. A standalone Asset can become Complete.

Apply the applicable replacement rule when archiving a replaced Atom.

## Planning Ticket containment

Keep the containment tree for any change. Move the companion folder with its Carrier.

When a parent moves from Draft to Backlog or In Queue, or from Backlog to In Queue, promote its contained planning Tickets with lower statuses. Preserve Assets, terminal statuses, and unpublished revisions of Tickets with a Current carrier.

When a parent becomes Done or Canceled, cancel every Current nonterminal descendant. Preserve the Status, Version, and history of terminal descendants. Reopening a Done or Canceled parent makes it In Queue and preserves the descendant tree and states.
