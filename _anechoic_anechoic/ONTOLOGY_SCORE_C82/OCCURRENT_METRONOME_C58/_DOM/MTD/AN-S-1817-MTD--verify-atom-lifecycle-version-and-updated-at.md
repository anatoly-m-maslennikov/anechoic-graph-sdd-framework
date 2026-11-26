---
atom_family: SPEC
atom_id: AN-S-1817
container:
  component: C58
tier: 4
context:
  lens: DOM/MTD
state:
  status: active
  version: 25
  updated_at: '2026-11-25T20:53:21.991115+00:00'
---
## Summary

Verify Atom lifecycle Version and Updated At

## Claim

### Prose Claim

This Evaluation checks persisted Atom lifecycle Version and Updated At against AN-S-1604 and AN-S-2589, using source carrier bytes and readback as evidence. Journal recording is independent and is not an acceptance gate for a verified lifecycle effect.

## Details

### Test cases and acceptance criteria

- For each admitted in-place edit, read back the carrier. Verify requested changes, preserve omitted properties and Version, and confirm Updated At equals the edit time. Verify a no-op retains Version and Updated At.
- Change a Current Status and archive a Current Atom. Read back each carrier; verify its resulting Status, unchanged Version and Updated At equal to the edit time. Verify against its source bytes that the archived predecessor preserves its base Atom ID, Version and unrelated content. Allow the requested Status and model-derived placement, destination, version-qualified Ref ID and filename; those do not create a new base Atom ID.
- For a Current Atom with unchanged Summary and revision identity, create a Draft. Verify the same ID and a Version one above the greatest occupied Version, including existing Drafts. For an ordinary promotion, verify the Draft Version is retained. Verify other Drafts remain byte-for-byte unchanged.
- For a proposed Summary change, verify that the same-ID revision route refuses the changed Summary. In the replacement route, verify a new Atom ID at Version 1 and the requested predecessor archival. Verify that the explicit identity observation under AN-S-1450 has no source effects and does not gate lifecycle operations.
- For composed Update, verify the selected Current's Status is captured and retained at promotion, with source archive preceding successor publication. Check that the supplied allowed Current Status is used, with no semantic assessment or classification gate. Verify each distinct eligible Current `IS_REPLACEMENT_FOR` target is archived before publication, and already Archived targets are not archived again.
- Compare persisted source bytes and readback to the requested changes; reject mismatched properties, identity, Version, Updated At, Status, or preservation of unrelated data. Record actual partial effects on a failed effect. A missing or failed Journal observation alone does not fail a verified effect.

Move a Carrier without editing its Atom and verify that Updated At is preserved. This Evaluation does not establish that a runtime execution occurred.
