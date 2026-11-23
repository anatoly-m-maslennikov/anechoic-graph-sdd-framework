---
atom_family: SPEC
atom_id: AN-S-3360
container:
  component: C14
tier: 3
context:
  lens: DevOps
state:
  status: "archived"
  version: 2
  updated_at: "2026-11-22T20:53:03.755820+00:00"
---

## Summary

Precompile Studio Python imports

## Claim

### Prose Claim

Precompile the installed Studio Python Modules and dependencies once
for the target interpreter and final installed paths. Build the cache
with the same source bytes that the staged runtime imports. Apply this
rule to all installed Studio entry points and their child processes.

Use the owned Python cache boundary in AN-S-1342. Keep runtime bytecode
writes disabled. Rebuild the cache when the installed interpreter or
source changes. Use a source hash to validate a cache that can outlive
its source installation.

Keep mounted Project sources outside the installed cache build. Verify
the staged runtime can import from its cache with writes disabled.

### Profilers

Include profilers only in diagnostic test images. Keep them out of any
candidate that can become the production image, including during its
release tests. Verify the source and dependency inventory of the exact
candidate before promotion.
