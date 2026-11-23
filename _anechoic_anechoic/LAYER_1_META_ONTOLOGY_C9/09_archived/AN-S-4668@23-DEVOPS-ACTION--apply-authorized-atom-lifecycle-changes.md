---
atom_family: SPEC
atom_id: AN-S-4668
container:
  component: C9
tier: 3
context:
  template: action
  lens: DevOps
state:
  status: archived
  version: 23
  updated_at: 2026-10-27 19:59:46 +0400
---
## Summary

Apply authorized Atom lifecycle changes

# Summary

Apply authorized Atom lifecycle changes

## Operation

Apply the requested Atom lifecycle operation. Create Draft from new Atom properties or a selected existing Atom by merging supplied properties and retaining omissions; derive filename and path. For a Current source with unchanged Summary and Content Role, create its same-ID Draft at Version N+1 once. Editing a Draft preserves its Version and Updated At. If Summary or Content Role changes, the result is a new identity promoted at Version 1; promotion does not increment Draft Version again.

Direct update edits the selected Draft, Current or Archived Atom in place, preserving Version and Updated At. Archive and Current Status changes preserve Version and Updated At. Update a Current Atom by creating its Draft, archiving the Current, and promoting the Draft with the same captured Current Status. Generic Promote accepts any supplied allowed Current Status.

Before publishing the Draft, resolve every distinct `IS_REPLACEMENT_FOR` target, including different IDs and many-to-one replacements. Archive each eligible Current target once and skip every target already Archived, including one archived by composed Update. Publish the Current successor only after those archives, then remove the Draft carrier. On an effect failure stop and report the actual completed and incomplete effects.

Move one selected existing Atom from its bound source to its destination scope, deriving the resulting path under applicable placement rules while preserving identity and content meaning. It does not perform Scope Unit operations or move other independent Atoms. Status changes act on one bound Atom; the caller composes any required containment cascade under CA-R-1521 and CA-D-461/CA-D-467, as specified by CA-O-127.

For missing or invalid input formats or allowed values, give a short explanation and request an additional input dictionary; wait for input. Cancellation is allowed while waiting, not during an Action. Apply the requested operation without a change-class or semantic gate, retry, rollback, recovery or repair. Attempt Journal observations of actual business events independently; recording failure is nonblocking.
