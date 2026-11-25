---
atom_family: SPEC
atom_id: AN-S-1853
container:
  component: C9
tier: 3
context:
  lens: DevOps
state:
  status: "archived"
  version: 25
  updated_at: "2026-11-25T20:09:43.072722+00:00"
---
## Summary

Keep Atom addresses consistent with carried Properties

## Claim

### Prose Claim


Atom Properties represented by a filename, matching directory name, or placement.


**every** Atom Property represented by a filename, matching directory name, **or** placement **must** agree with its canonical internal value under the applicable Delivery encoding.

- compare resolved values using the registered encoding; a Summary Slug is checked against its Summary serialization, **not** against identical raw text.
- a mismatch is invalid **and** **must** be reported; the address **must not** silently override the value carried inside the Atom.
- agreement checking does **not** authorize rewriting the Atom **or** address. corrections require the applicable authorized change.

When an authorized parent Directory Carrier move carries a Current descendant, store the descendant's calculated `Header.Destination.File.Name` and `.Path` for the resulting location. For a descendant carried with its existing terminal Status, preserve its Status, Version, Updated At and Content. Treat the destination-only rewrite as a physical placement update within the existing Version.
