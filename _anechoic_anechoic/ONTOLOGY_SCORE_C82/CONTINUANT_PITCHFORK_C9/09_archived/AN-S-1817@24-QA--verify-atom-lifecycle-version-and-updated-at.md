---
atom_family: SPEC
atom_id: AN-S-1817
container:
  component: C9
tier: 4
context:
  lens: QA
state:
  status: "archived"
  version: 24
  updated_at: "2026-11-25T20:53:21.919168+00:00"
---
## Summary

Verify Atom lifecycle Version and Updated At

## Claim

### Prose Claim

This Evaluation checks persisted Atom lifecycle Version and Updated At against AN-S-1604 and AN-S-2589, using source carrier bytes and readback as evidence. Journal recording is independent and is not an acceptance gate for a verified lifecycle effect.

## Details

### Test cases and acceptance criteria

- Edit a Draft, Current and Archived Atom directly in place. Read back each carrier and verify the requested properties and preserved omitted properties, unchanged Version and Updated At equal to the edit time.
- Change a Current Status and archive a Current Atom. Read back each carrier; verify its resulting Status, unchanged Version and Updated At equal to the edit time. Verify against its source bytes that the archived predecessor preserves its base Atom ID, Version and unrelated content. Allow the requested Status and model-derived placement, destination, version-qualified Ref ID and filename; those do not create a new base Atom ID.
- Create a Draft for a new version of a Current Atom with unchanged Summary and Content Role. Verify the same identity and Version N+1 at Draft creation. Promote it and verify the promoted Atom retains that Draft Version, with no second increment.
- Change the Draft Summary or Content Role relative to its source. Promote it and verify a new identity at Version 1.
- For composed Update, verify the selected Current's Status is captured and retained at promotion, with source archive preceding successor publication. Verify each distinct eligible Current `IS_REPLACEMENT_FOR` target is archived before publication, and already Archived targets are not archived again.
- Compare persisted source bytes and readback to the requested changes; reject mismatched properties, identity, Version, Updated At, Status, or preservation of unrelated data. Record actual partial effects on a failed effect. A missing or failed Journal observation alone does not fail a verified effect.

Move a Carrier without editing its Atom and verify that Updated At is preserved. This Evaluation does not establish that a runtime execution occurred.
